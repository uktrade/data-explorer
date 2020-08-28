// Buttons
var refreshButton = document.getElementById("refresh_button");
if (refreshButton) {
	refreshButton.addEventListener("click", function(e){
		document.getElementById("editor").setAttribute("action", "");
	});
}
var createButton = document.getElementById("create_button");
if (createButton) {
	createButton.addEventListener("click", function(e){
		document.getElementById("editor").setAttribute("action", "../new/");
	});
}

let save_button = document.getElementById("save_button");
if (save_button !== null) {
    save_button.addEventListener("click", function(e){
        document.getElementById("editor").setAttribute("action", "")
    });
}

let save_only = document.getElementById("save_only");
if (save_only !== null) {
    save_only.addEventListener("click", function(e){
        document.getElementById("editor").setAttribute("action", "")
    });
}

document.getElementById("download_csv").addEventListener("click", function(e){
    document.getElementById("editor").setAttribute("action", "../download?format=csv")
});

document.getElementById("download_excel").addEventListener("click", function(e){
    document.getElementById("editor").setAttribute("action", "../download?format=excel")
});

document.getElementById("download_json").addEventListener("click", function(e){
    document.getElementById("editor").setAttribute("action", "../download?format=json")
});

document.getElementById("show_schema_button")
    .addEventListener(
	"click",
	function(e) {
	    let element = document.getElementById("schema_frame");

	    if(element.getAttribute('schemaHidden') === null) {
		element.setAttribute('schemaHidden', true);
	    }

	    element.setAttribute(
		'src',
		'../schema-pane/' + document.getElementById('id_connection').value
	    );

	    let schemaHidden = element.getAttribute('schemaHidden');
	    
	    if(schemaHidden === "true") {
		element = document.getElementById("query_area");
		element.classList.remove("govuk-grid-column-full")
		element.classList.add("govuk-grid-column-two-thirds");
		
		element = document.getElementById("schema")
		element.classList.add("govuk-grid-column-one-third");
		element.style.display = "block";
		
		element = document.getElementById("show_schema_button");
		element.innerHTML = "Hide Schema"

		element = document.getElementById("schema_frame")
		element.setAttribute('schemaHidden', false);
		
	    } else {
		element = document.getElementById("query_area");
		element.classList.remove("govuk-grid-column-two-thirds");
		element.classList.add("govuk-grid-column-full")
		
		element = document.getElementById("schema")
		element.classList.remove("govuk-grid-column-one-third");
		element.style.display = "none";
		
		element = document.getElementById("show_schema_button");
		element.innerHTML = "Show Schema"

		element = document.getElementById("schema_frame")
		element.setAttribute('schemaHidden', true);
	    }
		   
	}
);


// Lifted from django-sql-explorer explorer.js
function updateQueryString(key, value, url) {
    // http://stackoverflow.com/a/11654596/221390
    if (!url) url = window.location.href;
    var re = new RegExp("([?&])" + key + "=.*?(&|#|$)(.*)", "gi"),
        hash = url.split('#');

    if (re.test(url)) {
        if (typeof value !== 'undefined' && value !== null)
            return url.replace(re, '$1' + key + "=" + value + '$2$3');
        else {
            url = hash[0].replace(re, '$1$3').replace(/(&|\?)$/, '');
            if (typeof hash[1] !== 'undefined' && hash[1] !== null)
                url += '#' + hash[1];
            return url;
        }
    }
    else {
        if (typeof value !== 'undefined' && value !== null) {
            var separator = url.indexOf('?') !== -1 ? '&' : '?';
            url = hash[0] + separator + key + '=' + value;
            if (typeof hash[1] !== 'undefined' && hash[1] !== null)
                url += '#' + hash[1];
            return url;
        }
        else
            return url;
    }
};

let fetchPage = document.getElementById('fetch-page');
if (fetchPage !== null) {
    fetchPage.addEventListener('submit', function (e) {
        e.preventDefault();

        let editor = document.getElementById('editor');
        let queryPage = document.getElementById('query-page');
        let queryRows = document.getElementById('query-rows');

        if (editor != null && queryPage !== null && queryRows !== null) {
            editor.action = updateQueryString(
                'page',
                queryPage.value,
                updateQueryString(
                    'rows',
                    queryRows.value,
                    '.'
                )
            );
            editor.submit();
        }
    });
}


// SQL Editor
import * as ace from 'ace-builds'
import 'ace-builds/src-noconflict/mode-sql'
import 'ace-builds/src-noconflict/theme-chrome'
import 'ace-builds/src-noconflict/ext-language_tools'
import sqlFormatter from "sql-formatter";

var editor = ace.edit("ace-sql-editor", {
	mode: "ace/mode/sql",
	theme: "ace/theme/chrome",
	maxLines: 10,
	minLines: 10,
	fontSize: 18,
	showLineNumbers: false,
	showGutter: false,
	enableLiveAutocompletion: true,
	showPrintMargin: false
});

editor.commands.removeCommand(editor.commands.byName.indent);
editor.commands.removeCommand(editor.commands.byName.outdent);

var textarea = document.getElementsByName("sql")[0];
editor.getSession().on("change", function () {
    textarea.value = editor.getSession().getValue();
});

function update() {
    // adjust size to parent box on show schema
    editor.resize()

    // populate default message if required
    var shouldShow = !editor.session.getValue().length;
    var node = editor.renderer.emptyMessageNode;
    if (!shouldShow && node) {
        editor.renderer.scroller.removeChild(editor.renderer.emptyMessageNode);
        editor.renderer.emptyMessageNode = null;
    } else if (shouldShow && !node) {
        node = editor.renderer.emptyMessageNode = document.createElement("div");
        node.textContent = "Write your query here"
        node.className = "ace_emptyMessage"
        node.style.padding = "0 9px"
        node.style.position = "absolute"
        node.style.zIndex = 9
        node.style.opacity = 0.5
        editor.renderer.scroller.appendChild(node);
    }
}
editor.on("input", update);
setTimeout(update, 100);

document.getElementById("format_button")
    .addEventListener("click", function(e) {
        var sql = editor.getSession().getValue()
        var formatted_sql = sqlFormatter.format(sql)
        editor.getSession().setValue(formatted_sql)
	}
);

