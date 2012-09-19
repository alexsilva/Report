$(":input[type='checkbox']").wijcheckbox();
$("#project_id").wijdropdown();
$("#id_period_month").wijdropdown();
$("#id_period_year").wijdropdown();
$(":input[type='submit']").button();

var oTable = $('#list_table').dataTable({
  "oLanguage": {
  "sUrl": "/static/js/dataTable.oLanguage.txt"
  },
  "bJQueryUI": true,
  "aLengthMenu": [[25, 50, 100, -1], [25, 50, 100, "Todos"]],
  "bAutoWidth": false,
  "bStateSave": true,
  "iDisplayLength": 25,

  "aoColumns": [
  {% for header in  headers %}
	{"sTitle": "{{ header }}", "sClass":{% ifequal header "Assunto" %}"left"{% else %}"center"{% endifequal %} },
  {% endfor %}
  ],

  "aaData": [
  {% for slist in rlist %} [
	{% for item in slist %}
	  {% if item.link and item.label %}'<a href="{{item.link}}" target="_blank">{{item.label}}</a>'
	  {% else %}"{{ item }}"{% endif %},
	{% endfor %}],
  {% endfor %}]
});

var report = new function() {
  this.namespace = {
	check_status: function() {
	  var totalHours = parseFloat("{{params.statistic.total_hours}}".replace(",","."))
	  var yearlyRemainder = parseFloat("{{params.statistic.yearly_remainder}}".replace(",","."))
	  var monthlyRemainder = parseFloat("{{params.statistic.remainder}}".replace(",","."))
	  var yearlyActive = "{{params.statistic.yearlyplan.is_active}}"
	  var monthValid = "{{params.statistic.checkMonthYear}}"
	  var yearlyReport = parseInt("{{params.yearly_report}}")
	  var message = ""
	  
	  if (yearlyActive == "True") {
		if ( yearlyReport ) {
		  if (yearlyRemainder < 0.0) message = "O máximo de horas para o 'plano anual' foi excedido.";
		  if (yearlyRemainder == 0.0) message = "O máximo de horas para o 'plano anual' foi alcançado.";
		} else {
		  if (monthlyRemainder < 0.0) message = "O máximo de horas para o 'plano mensal' já foi excedido.";
		  if (monthlyRemainder == 0.0) message = "O máximo de horas para o 'plano mensal' já foi alcançado.";
		  
		  if (totalHours <= 0.0 && monthValid == "True") {
			message = "O total de horas para esse mês é menor ou igual a zero."
			message += "\n  Contate o administrado para resolver o problema."
		  }
		}
		if ( message ) alert( message );
	  }
	  },
	  // desativa um objeto(element), marcando o checkbox alvo.
	  disable : function(element_id, checkbox) {
		if (element_id[0] != "#") element_id = "#"+element_id
		var object = $( element_id );
		if ($( checkbox ).is(":checked")) {
		  object.attr('disabled', 'disabled');
		} else {
		  object.removeAttr('disabled');
		}
	  },
	  init: function() {
		var _this = this;
		//var checkbox = $("#yearly_report");
		//checkbox.click(function() {
		  //_this.disable("id_period_month", this);
		//});
		//this.disable("id_period_month", checkbox);
		// faz a verifiação dos dados do relatório.
		setTimeout(this.check_status, 1000);
	}
  }
}
report.namespace.init();