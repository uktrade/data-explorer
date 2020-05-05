import { concat, interval } from 'rxjs';
import { map, catchError, switchMap } from 'rxjs/operators';
import { ajax } from 'rxjs/ajax';

Vue.component('update-record', {
  props: {
    "record-data": {
      type: String,
      required: true
    },
    "regenarate-url": {
      type: String,
      required: true
    },
    "edit-url": {
      type: String,
    },
    "update-url": {
      type: String,
      required: true
    },
    "poll-interval": {
      type: Number,
      default: 1000
    }
  },
  data: function() {
    return {
      responseData: {},
      subscription: null
    };
  },
  created: function() {
    this.responseData = JSON.parse(this.recordData);
    if(!this.is_document_available()) {
      this.subscription = this.updateRecord();
      this._subscribeTO();
    }
  },
  computed: {
    created_at: function() {
      if (this.responseData.document_created_at) {
        const date = new Date(this.responseData.document_created_at);
        return `${date.toDateString()} ${date.toLocaleTimeString('uk-UK')}`;
      }
    }
  },
  delimiters: ['[[', ']]'],
  template: `<ul class="govuk-list">
      <li>
        <a v-if="is_document_available()" v-bind:href="responseData.download_url" class="govuk-link govuk-link--no-visited-state">Download</a>
        <div v-else-if="is_document_unavailable()" class="govuk-text">Error document unavailable</div>
        <div v-else-if="is_document_generating()" class="govuk-text">Updating document</div>
        <div v-else class="govuk-text">Error document unavailable</div>
      </li>
      <li v-if="editUrl">
        <a v-bind:href="editUrl" class="govuk-link govuk-link--no-visited-state">Edit</a>
      </li>
      <li v-if="!is_document_generating() || is_document_unavailable()">
        <a href="#" v-on:click.stop.prevent="regenarateRecord" class="govuk-link govuk-link--no-visited-state">Regenerate</a>
      </li>
      <li class="govuk-!-padding-top-2" v-if="responseData.document_created_at">
          <p class="govuk-body govuk-!-font-size-14">Last updated:<br />[[created_at]]</p>
      </li>
    </ul>
  `,
  methods: {
    regenarateRecord: function() {
      this.responseData.document_status = 'generating'
      let generate$ = ajax(this.regenarateUrl).pipe(
        map(res => res),
        catchError(error => {
          console.log('error: ', error);
          return of(error);
        })
      );

      this.subscription = concat(generate$, this.updateRecord());
      this._subscribeTO();
    },
    updateRecord: function() {
      return interval(this.pollInterval).pipe(
        switchMap(() =>
          ajax.getJSON(this.updateUrl)
        ),
        map(res => res),
        catchError(error => {
          console.log('error: ', error);
          return of(error);
        })
      );
    },
    _subscribeTO: function() {
      this.subscription = this.subscription.subscribe(res => {
        if (res && res.document_status === 'available') {
            this.responseData = res;
            this.subscription.unsubscribe()
        }
      });
    },
    is_document_available: function() {
      return this.responseData.document_status === 'available';
    },
    is_document_generating: function() {
      return this.responseData.document_status === 'generating';
    },
    is_document_unavailable: function() {
      return this.responseData.document_status === 'unavailable';
    },
    beforeDestroy: () => {
      if (this.subscription) this.subscription.unsubscribe();
    }
  }
});
