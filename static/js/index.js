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
