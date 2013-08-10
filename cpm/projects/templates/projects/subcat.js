/**
 * User: goldhand
 * Date: 8/9/13
 * Time: 10:52 PM
 */


var tcl = $('#task-category-list').find('ul').each(function(i) { console.log($(this).parent().attr('id')); console.log($(this).sortable('toArray'));});
