// dd/mm/YYY
jQuery.extend(jQuery.fn.dataTableExt.oSort, {
  "date-uk-pre": function ( a ) {
	var ukDatea = a.split('/');
	return (ukDatea[2] + ukDatea[1] + ukDatea[0]) * 1;
  },
  
  "date-uk-asc": function ( a, b ) {
	return ((a < b) ? -1 : ((a > b) ? 1 : 0));
  },
  
  "date-uk-desc": function ( a, b ) {
	return ((a < b) ? 1 : ((a > b) ? -1 : 0));
  }
});
// mm/YYY
jQuery.extend( jQuery.fn.dataTableExt.oSort, {
  "monthYear-pre": function ( s ) {
	var a = s.split('/');
	// Date uses the American "MM DD YY" format
	return (a[1] + a[0]) *1;
  },

  "monthYear-asc": function ( a, b ) {
	return ((a < b) ? -1 : ((a > b) ? 1 : 0));
  },

  "monthYear-desc": function ( a, b ) {
	return ((a < b) ? 1 : ((a > b) ?  -1 : 0));
  }
});
// nn,nn
jQuery.extend( jQuery.fn.dataTableExt.oSort, {
    "formatted-num-pre": function ( a ) {
        a = (a==="-") ? 0 : a.replace( /[^\d\-\.]/g, "" );
        return parseFloat( a );
    },
 
    "formatted-num-asc": function ( a, b ) {
        return a - b;
    },
 
    "formatted-num-desc": function ( a, b ) {
        return b - a;
    }
});
// Data type auto-detect.
jQuery.fn.dataTableExt.aTypes.unshift(
  function ( sData ) {
	var monthYearPattern = /\d{2}\/\d{4,}/;
	var fullYearPattern = /\d{2}\/\d{2}\/\d{4,}/;
	var commaNumPaterrn = /\d+,\d+/;
	
	if (commaNumPaterrn.test( sData )){
	  return "formatted-num";
	}
	
	if (fullYearPattern.test( sData )){
	  return "date-uk";
	}
	if (monthYearPattern.test( sData )) {
	  return "monthYear";
	}
	return null;
});