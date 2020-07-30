// Vue
import VueRx from 'vue-rx'
import Vue from 'vue'
window.Vue = Vue;
Vue.use(VueRx)

var createButton = document.getElementById("create_button");
if (createButton) {
	createButton.addEventListener("click", function(e){
		document.getElementById("editor").setAttribute("action", "../new/");
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
		'../schema/' + document.getElementById('id_connection').value
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
