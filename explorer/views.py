import re
from collections import Counter

import six
from django.contrib.auth.views import LoginView
from django.core import serializers
from django.core.exceptions import FieldDoesNotExist
from django.core.paginator import Paginator
from django.db import DatabaseError
from django.db.models import Count
from django.forms.models import model_to_dict
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import CreateView, DeleteView

from explorer import app_settings
from explorer.connections import connections
from explorer.exporters import get_exporter_class
from explorer.forms import QueryForm
from explorer.models import FieldSchema, ModelSchema, Query, QueryLog
from explorer.schema import schema_info
from explorer.utils import (
    fmt_sql,
    get_total_pages,
    url_get_log_id,
    url_get_page,
    url_get_params,
    url_get_query_id,
    url_get_rows,
    url_get_show,
)


class SafeLoginView(LoginView):
    template_name = 'admin/login.html'


def _export(request, query, download=True):
    format = request.GET.get('format', 'csv')
    exporter_class = get_exporter_class(format)
    query.params = url_get_params(request)
    delim = request.GET.get('delim')
    exporter = exporter_class(query)
    try:
        output = exporter.get_output(delim=delim)
    except DatabaseError as e:
        msg = "Error executing query %s: %s" % (query.title, e)
        return HttpResponse(msg, status=500)
    response = HttpResponse(output, content_type=exporter.content_type)
    if download:
        response['Content-Disposition'] = 'attachment; filename="%s"' % (exporter.get_filename())
    return response


class DownloadQueryView(View):
    def get(self, request, query_id, *args, **kwargs):
        query = get_object_or_404(Query, pk=query_id)
        resp = _export(request, query)
        if (
            isinstance(resp, HttpResponse)
            and resp.status_code == 500
            and "Error executing query" in resp.content.decode(resp.charset)
        ):
            return HttpResponseRedirect(reverse_lazy('query_detail', kwargs={'query_id': query_id}))
        return resp


class DownloadFromSqlView(View):
    def post(self, request, *args, **kwargs):
        sql = request.POST.get('sql')
        connection = request.POST.get('connection')
        query = Query(sql=sql, connection=connection, title='')
        ql = query.log(request.user)
        query.title = 'Playground - %s' % ql.id
        return _export(request, query)


class SchemaView(View):
    @method_decorator(xframe_options_sameorigin)
    def dispatch(self, *args, **kwargs):
        return super(SchemaView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        connection = kwargs.get('connection')
        if connection not in connections:
            raise Http404
        schema = schema_info(connection)
        if schema is not None:
            return render(None, 'explorer/schema.html', {'schema': schema_info(connection)})
        else:
            return render(None, 'explorer/schema_building.html')


@require_POST
def format_sql(request):
    sql = request.POST.get('sql', '')
    formatted = fmt_sql(sql)
    return JsonResponse({"formatted": formatted})


class ListQueryView(ListView):
    def recently_viewed(self):
        qll = (
            QueryLog.objects.filter(run_by_user=self.request.user, query_id__isnull=False)
            .order_by('-run_at')
            .select_related('query')
        )
        ret = []
        tracker = []
        for ql in qll:
            if len(ret) == app_settings.EXPLORER_RECENT_QUERY_COUNT:
                break

            if ql.query_id not in tracker:
                ret.append(ql)
                tracker.append(ql.query_id)
        return ret

    def get_context_data(self, **kwargs):
        context = super(ListQueryView, self).get_context_data(**kwargs)
        context['object_list'] = self._build_queries_and_headers()
        context['recent_queries'] = self.recently_viewed()
        context['tasks_enabled'] = app_settings.ENABLE_TASKS
        return context

    def get_queryset(self):
        qs = Query.objects.all()
        return qs.annotate(run_count=Count('querylog'))

    def _build_queries_and_headers(self):
        """
        Build a list of query information and headers (pseudo-folders)
        for consumption by the template.

        Strategy: Look for queries with titles of the form "something - else"
        (eg. with a ' - ' in the middle)
        and split on the ' - ', treating the left side as a "header" (or folder). Interleave the
        headers into the ListView's object_list as appropriate. Ignore headers that only have one
        child. The front end uses bootstrap's JS Collapse plugin, which necessitates generating CSS
        classes to map the header onto the child rows, hence the collapse_target variable.

        To make the return object homogeneous, convert the object_list models into dictionaries for
        interleaving with the header "objects". This necessitates special handling of 'created_at'
        and 'created_by_user' because model_to_dict doesn't include non-editable fields (created_at)
        and will give the int representation of the user instead of the string representation.

        :return: A list of model dictionaries representing all the query objects,
        interleaved with header dictionaries.
        """

        dict_list = []
        rendered_headers = []
        pattern = re.compile(r'[\W_]+')

        headers = Counter([q.title.split(' - ')[0] for q in self.object_list])

        for q in self.object_list:
            model_dict = model_to_dict(q)
            header = q.title.split(' - ')[0]
            collapse_target = pattern.sub('', header)

            if headers[header] > 1 and header not in rendered_headers:
                dict_list.append(
                    {
                        'title': header,
                        'is_header': True,
                        'is_in_category': False,
                        'collapse_target': collapse_target,
                        'count': headers[header],
                    }
                )
                rendered_headers.append(header)

            model_dict.update(
                {
                    'is_in_category': headers[header] > 1,
                    'collapse_target': collapse_target,
                    'created_at': q.created_at,
                    'is_header': False,
                    'run_count': q.run_count,
                    'created_by_user': six.text_type(q.created_by_user.email)
                    if q.created_by_user
                    else None,
                }
            )

            dict_list.append(model_dict)
        return dict_list

    model = Query


class ListQueryLogView(ListView):
    def get_queryset(self):
        kwargs = {'sql__isnull': False}
        if url_get_query_id(self.request):
            kwargs['query_id'] = url_get_query_id(self.request)
        return QueryLog.objects.filter(**kwargs).all()

    context_object_name = "recent_logs"
    model = QueryLog
    paginate_by = 20


class CreateQueryView(CreateView):
    def form_valid(self, form):
        form.instance.created_by_user = self.request.user
        return super().form_valid(form)

    def post(self, request):
        ret = super().post(request)
        if self.get_form().is_valid():
            show = url_get_show(request)
            query, form = QueryView.get_instance_and_form(request, self.object.id)
            success = form.is_valid() and form.save()
            vm = query_viewmodel(
                request.user,
                query,
                form=form,
                run_query=show,
                rows=url_get_rows(request),
                page=url_get_page(request),
                message="Query created." if success else None,
                log=False,
            )
            if vm['form'].errors:
                self.object.delete()
            return render(self.request, 'explorer/query.html', vm)
        return ret

    form_class = QueryForm
    template_name = 'explorer/query.html'


class DeleteQueryView(DeleteView):

    model = Query
    success_url = reverse_lazy("explorer_index")


class PlayQueryView(View):
    def get(self, request):
        if url_get_query_id(request):
            query = get_object_or_404(Query, pk=url_get_query_id(request))
            return self.render_with_sql(request, query, run_query=False)

        if url_get_log_id(request):
            log = get_object_or_404(QueryLog, pk=url_get_log_id(request))
            query = Query(sql=log.sql, title="Playground", connection=log.connection)
            return self.render_with_sql(request, query)

        return render(
            self.request, 'explorer/play.html', {'title': 'Playground', 'form': QueryForm()}
        )

    def post(self, request):
        sql = request.POST.get('sql')
        show = url_get_show(request)
        query = Query(sql=sql, title="Playground", connection=request.POST.get('connection'))
        run_query = True if show else False
        return self.render_with_sql(request, query, run_query=run_query)

    def render_with_sql(self, request, query, run_query=True):
        rows = url_get_rows(request)
        page = url_get_page(request)
        form = QueryForm(request.POST if len(request.POST) else None, instance=query)
        return render(
            self.request,
            'explorer/play.html',
            query_viewmodel(
                request.user,
                query,
                title="Playground",
                run_query=run_query and form.is_valid(),
                rows=rows,
                page=page,
                form=form,
            ),
        )


class QueryView(View):
    def get(self, request, query_id):
        query, form = QueryView.get_instance_and_form(request, query_id)
        query.save()  # updates the modified date
        show = url_get_show(request)
        rows = url_get_rows(request)
        page = url_get_page(request)
        vm = query_viewmodel(
            request.user, query, form=form, run_query=show, rows=rows, page=page, method="GET"
        )
        return render(self.request, 'explorer/query.html', vm)

    def post(self, request, query_id):
        show = url_get_show(request)
        query, form = QueryView.get_instance_and_form(request, query_id)
        success = form.is_valid() and form.save()
        vm = query_viewmodel(
            request.user,
            query,
            form=form,
            run_query=show,
            rows=url_get_rows(request),
            page=url_get_page(request),
            message="Query saved." if success else None,
        )
        return render(self.request, 'explorer/query.html', vm)

    @staticmethod
    def get_instance_and_form(request, query_id):
        query = get_object_or_404(Query, pk=query_id)
        query.params = url_get_params(request)
        form = QueryForm(request.POST if len(request.POST) else None, instance=query)
        return query, form


def query_viewmodel(
    user,
    query,
    title=None,
    form=None,
    message=None,
    run_query=True,
    rows=app_settings.EXPLORER_DEFAULT_ROWS,
    timeout=app_settings.EXPLORER_QUERY_TIMEOUT_MS,
    page=1,
    method="POST",
    log=True,
):
    res = None
    ql = None
    error = None
    if run_query:
        try:
            if log:
                res, ql = query.execute_with_logging(user, page, rows, timeout)
            else:
                res = query.execute(page, rows, timeout)
        except DatabaseError as e:
            error = str(e)
    if error and method == "POST":
        form.add_error('sql', error)
        message = "Query error"
    has_valid_results = not error and res and run_query
    ret = {
        'tasks_enabled': app_settings.ENABLE_TASKS,
        'params': query.available_params(),
        'title': title,
        'query': query,
        'form': form,
        'message': message,
        'rows': rows,
        'page': page,
        'data': res.data if has_valid_results else None,
        'headers': res.headers if has_valid_results else None,
        'total_rows': res.row_count if has_valid_results else None,
        'duration': res.duration if has_valid_results else None,
        'has_stats': len([h for h in res.headers if h.summary]) if has_valid_results else False,
        'ql_id': ql.id if ql else None,
        'unsafe_rendering': app_settings.UNSAFE_RENDERING,
    }
    ret['total_pages'] = get_total_pages(ret['total_rows'], rows)
    return ret


class ConnectionBrowserListView(TemplateView):

    template_name = "browser/connection_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['connections'] = app_settings.EXPLORER_CONNECTIONS
        return context


class TableBrowserListView(TemplateView):

    template_name = "browser/table_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        connection = self.kwargs['connection']
        context['tables'] = schema_info(connection)
        context['connection'] = connection
        return context


class TableBrowserDetailView(ListView):

    template_name = "browser/table.html"
    COLUMN_MAPPING = {
        'CharField': 'character',
        'TextField': 'text',
        'IntegerField': 'integer',
        'FloatField': 'float',
        'BooleanField': 'boolean',
        'DateField': 'date',
        'TimestampField': 'date',
    }
    MAXIMUM_FILTER_VALUES = 100

    def get_model(self):
        schema = self.kwargs['schema']
        table = self.kwargs['table']

        columns = schema_info(self.kwargs['connection'], schema, table)
        table_name = f'"{schema}"."{table}"'

        try:
            model = ModelSchema.objects.get(name=table_name)
        except ModelSchema.DoesNotExist:
            model = ModelSchema.objects.create(name=table_name)

        for column in columns:
            # Django automatically adds a field called id to all models if a primary key isn't
            # specified so we need to skip adding this to the dynamic model
            if column.name == 'id':
                continue
            try:
                field = FieldSchema.objects.get(name=column.name)
            except FieldSchema.DoesNotExist:
                field = FieldSchema.objects.create(
                    name=column.name, data_type=self.COLUMN_MAPPING[column.type]
                )

            try:
                model.add_field(field)
            except Exception:
                pass

        Model = model.as_model()
        Model.objects = Model.objects.using(self.kwargs['connection'])
        Model._meta.db_table = table_name

        return Model

    def get_queryset(self):
        if not self.model:
            self.model = self.get_model()
        filters = {}
        for filter_field, filter_value in self.request.GET.items():
            if not filter_value:
                continue
            try:
                field = self.model._meta.get_field(filter_field)
            except FieldDoesNotExist:
                continue
            else:
                filters[filter_field] = field.to_python(filter_value)

        queryset = self.model.objects.filter(**filters)
        order_by = self.request.GET.get('order_by')
        if order_by:
            return queryset.order_by(order_by)
        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        paginator = Paginator(
            serializers.serialize('python', queryset), app_settings.TABLE_BROWSER_LIMIT
        )
        page_number = self.request.GET.get('page')
        fields = [f for f in self.model._meta.get_fields() if f.name != 'id']

        ctx['schema_name'] = self.kwargs['schema']
        ctx['table_name'] = self.kwargs['table']
        # Sets a tuple of (field name, sorted distinct values) for all fields to allow filtering
        ctx['fields'] = [
            (
                f.name,
                sorted([str(x) for x in queryset.values_list(f.name, flat=True).distinct()])[
                    : self.MAXIMUM_FILTER_VALUES
                ],
            )
            for f in fields
        ]
        ctx['connection'] = self.kwargs['connection']
        ctx['objects'] = paginator.get_page(page_number)
        return ctx
