/**
 * goldhand
 * Date: 7/21/13
 * Time: 2:15 PM
 * To change this template use File | Settings | File Templates.
 */
var project_id;
var project_summary_json = {};
var task_form_url;
var category_form_url;
var project_form_url;

var project_url_id = GetURLParameter('project');
var change_order_url_id = GetURLParameter('change_order');

$(window).scroll(function(){
    $(".form-fixed").css("top",Math.max(40,200-$(this).scrollTop()));
    $("#step-nav").css("top",Math.max(0,160-$(this).scrollTop()));
});


function allDescendants (node, project_data) {
    var list_item = '<li id="cat_' + 'id=' + node['id'] + '">'
        + '<a href="' + node['update_url'] + '">'
        + node['title']
        + '</a><ul class="nav nav-list">';

    if (project_data[node['id']]) {
        list_item += project_data[node['id']] ;

    }
    if(node.children) {
        for (var i = 0; i < node.children.length; i++) {
            var child = node.children[i];
            list_item += allDescendants(child, project_data);
        }
        list_item += '</ul>';
    }
    list_item += '</li>';
    return list_item
}

Array.prototype.findInArray =function(propName,value)
    {
        var res={};
        if(propName && value)
        {
          for (var i=0; i<this.length; i++)
          {
            if(this[i][propName]==value)
            {
               res = this[i];
               break;
            }
          }
        }
        return res;
    }

function descendantItemToList(item) {
    var descendantsList = [];
    descendantsList.push(item);
    for (var i = 0; i < item.children.length; i++) {
        var child = descendantItemToList(item.children[i]);
        console.log(child);
        descendantsList.push(child[0]);
        if (child[1]) {
            for (var a = 0; a < child.slice(1).length; a++) {
                descendantsList.push(child.slice(1)[a]);
            }
        }
    }
    return descendantsList;
}
function descendantsToList(list) {
    var descendantsList = [];
    for (var i = 0; i < list.length; i++) {
        var listItem = descendantItemToList(list[i]);
        for (var a = 0; a < listItem.length; a++) {
            descendantsList.push(listItem[a]);
        }
    }
    descendantsList = descendantsList.concat();
    return descendantsList;
}


$(function () {
    if (project_url_id) {

        project_id = project_url_id;
        $('#step-nav a[href="#new-task"]').parent().removeClass('disabled');
        project_form_url = '/cpm/update/' + project_url_id + '/';
        getTaskForm(task_form_url);

        if (change_order_url_id) {
            getProjectCOSummary(change_order_url_id);
            showStep(2);
            $('#step-nav a[href="#new-project"]').parent().addClass('disabled');
            $('.page-header h1').replaceWith('<h1>Change Order</h1>');
        }
        else {
            getProjectSummary(project_id);
            $('#step-nav a[href="#new-category"]').parent().removeClass('disabled');
            // Have to replace the OG form, therwise 2 csrf tokens are sent
            getProjectForm(project_form_url);
            getTaskCategoryForm(category_form_url);
        }
    }
});

// Temp hack for updating projects looks in url for ?project=pk
function GetURLParameter(sParam) {
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++) {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam) {
            return decodeURIComponent(sParameterName[1]);
        }
    }
}


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
$('#task-list').sortable({
    axis: 'y',
    containment: 'parent',
    delay: 50,
    distance: 10
});
$('#task-list').on("sortupdate", function (event, ui) {

    var task_order = [];
    var taskList = $(this).sortable('toArray');
    for (var i = 0; i < taskList.length; i++) {
        var task_id = taskList[i].split('_')[1].split('=')[1];
        task_order.push(task_id);
    }

    var cookie = 'csrfmiddlewaretoken=' + getCookie('csrftoken') + '&';
    var ajaxPost = cookie + 'task_order=' + task_order;
    $.ajax({ url: '/cpm/projects/set_task_order/' + project_id + '/',
        type: 'POST',
        data: ajaxPost,
        success: function (data) {
            getProjectSummary(project_id, 1, 1);
        },
        error: function (data) {
        }
    });
});

$('#task-category-list').sortable({
    connectWith: 'parent',
    delay: 50,
    distance: 10,
    placeholder: 'placeholder',
    dropOnEmpty: true,
    items: 'li[id^="cat"]'
});

var devList = [];
$('#task-category-list').on("sortupdate", function (event, ui) {

    var formCount = 0;
    var jsonList = descendantsToList(project_summary_json);
    console.log(jsonList);
    var catList = $(this).sortable('widget').find('li[id^="cat"]');

    var cats = [];

    for (var i = 0; i < catList.length; i++) {

        var $catElem = $(catList[i]);
        var cat_id = $catElem.attr('id').split('_')[1].split('=')[1];
        var jsonItem = jsonList.findInArray('id', cat_id);
        if ($catElem.parent().parent('[id^="cat"]')[0]) {
            var cat_parent = $($catElem.parent().parent('[id^="cat"]')[0])
                .attr('id').split('_')[1].split('=')[1];
            devList.push($($catElem.parent().parent('[id^="cat"]')));
            console.log(cat_parent);
        } else {
            cat_parent = null;
        }
        var cat = {
            'id': cat_id,
            'title': jsonItem.title_url,
            'order': i,
            'parent': cat_parent
        };
        cats.push(cat);
        formCount += 1;
    }

    var cats_str = [];
    for (i = 0; i < cats.length; i++) {
        var cat_keys = Object.keys(cats[i]);
        var prefix = 'form-' + i + '-';
        for (var a = 0; a < cat_keys.length; a++) {
            cats_str.push(prefix + [cat_keys[a], cats[i][cat_keys[a]]].join('='));
        }
    }
    data_list=cats_str;

    var cookie = 'csrfmiddlewaretoken=' + getCookie('csrftoken') + '&';
    var extraPost = 'form-MAX_NUM_FORMS=1000&form-TOTAL_FORMS=' + formCount + '&form-INITIAL_FORMS=' + formCount + '&';
    var ajaxPost = cookie + extraPost + cats_str.join('&');
    console.log(ajaxPost);
    $.ajax({ url: '/cpm/tasks/category/manage/',
        type: 'POST',
        data: ajaxPost,
        success: function (data) {
            console.log('success' + data['success']);
            getProjectSummary(project_id, 1, 1);
        },
        error: function (data) {
            console.log(data['error']);
        }
    })
});

var list1;
var data_list = [];
function getProjectSummary(project_id, catsToo, tasksToo) {
    catsToo = catsToo || 0;
    console.log(catsToo);
    tasksToo = tasksToo || 0;
    console.log(tasksToo);
    if (change_order_url_id) {
        getProjectCOSummary(change_order_url_id);

    } else {
    var JSON_url = '/cpm/projects/json/' + project_id + '/';
    var project_data = {};
    var task_data = [];
    //var task_list = [];
    $.getJSON(JSON_url, function (data) {
        var i = 0;
        $.each(data['category_totals'], function (key, value) {
            var task_list = [];
            var list1_data = [];
            var list1_data_simple = [];
            $.each(value['task_set'], function (key_1, value_1) {
                task_list.push(value_1);

            });
            task_list = task_list.sort(function (a, b) {
                if (a._order > b._order) return 1;
                if (a._order < b._order) return -1;
                return 0;
            });
            $.each(task_list, function (key_1, value_1) {
                var list_item = '<li id="task_' + 'id=' + value_1['id'] + '"><a href="' + value_1['update_url'] + '">'
                    + value_1['title'] + '</a>'
                    + value_1['description']
                    + '<ul class="unstyled">'
                    + '<li class="cat-expense">Expense: &nbsp;$' + value_1.expense + '</li>'
                    + '<li class="cat-price">Markup: &nbsp;&nbsp;&nbsp;$' + value_1.price + '</li>'
                    + '</ul>'
                    + '</li>'

                var list_item_simple = '<li class="disabled" id="task_' + 'id=' + value_1['id'] + '"><a href="' + value_1['update_url'] + '">' + value_1['title'] + '</a></li>';

                list1_data.push(list_item);
                list1_data_simple.push(list_item_simple);
            });
            task_data.push(list1_data.join(''));
            project_data[key] = '<ul class="nav nav-list">' + list1_data_simple.join('')
                // Spacing between label and $
                + '<li class="cat-expense">Expense: &nbsp;$' + value.expense + '</li>'
                + '<li class="cat-price">Markup: &nbsp;&nbsp;&nbsp;$' + value.price + '</li>'
                + '<li class="cat-total">Total: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$' + value.total + '</li>'
            + '</ul>'
            ;
            i++;
        });
        if (tasksToo != 1) {
            $('#task-list').html(task_data.join(''));
            console.log('Changing Tasks Too!')
        }

        $.getJSON('/cpm/tasks/category/alt/', function (data) {
            var list_data = [];
            var cat_list_data = [];
            project_summary_json = data['category_list'];
            var project_summary_list = [];
            $.each(data['category_list'], function (key, value) {
                project_summary_list.push(value);
            });
            project_summary_list = project_summary_list.sort(function (a, b) {
                if (a.order > b.order) return 1;
                if (a.order < b.order) return -1;
                return 0;
            });
            list1 = project_summary_list;
            $.each(project_summary_list, function (key, value) {
                var list_item = allDescendants(value, project_data);
                var cat_list_item = allDescendants(value, []);
                list_data.push(list_item);
                cat_list_data.push(cat_list_item);
            });
            if (catsToo != 1) {
                $('#task-category-list').html(cat_list_data.join(''));
                console.log('Changing Cats Too!')
            }
            $('#project-summary').html(list_data.join(''));


        });
        var versions = [];
        $.each(data['versions'], function(key, value) {
            var instance = $.parseJSON(value.instance);
            var created  = value.created.split('T');
            var version = value.version;
            console.log(instance);
            console.log(created);
            versions.push(version + '"><a href="#">Date: ' + created[0] + ' Time: ' + created[1] );
        });

        versions = '<li id="version-' + versions.join('</a></li><li id="version-');
        $('#version-list').html(versions);
        $('#project-summary-fields').html(
                '<a class="toggle-table pull-right" data-target="#"><i class="icon-collapse-alt"></i></a>'
                + '<div class="collapse">'
                + '<h4>'+ data.title + '</h4>'
                + '<h5>' + data.username + '</h5>'
                + '<ul class="unstyled">'
                    + '<li>Expense: $' + data.expense + '</li>'
                    + '<li>Markup: $' + data.price + '</li>'
                    + '<li>Total: $' + data.total + '</li>'
                + '</ul>'
                + '<p>' + data.description + '</p>'
            );

    });//project summary json

    }

}
$('#project-summary').parent().on('click', '.toggle-table', function(e) {
    if ($(this).find('i').hasClass('icon-collapse-alt')) {
        $(this).parent().parent().find('.collapse').collapse('hide');
        $(this).parent().parent().find('i').removeClass('icon-collapse-alt icon-expand-alt').addClass('icon-expand-alt')
    } else {
        $(this).parent().parent().find('.collapse').collapse('show');
        $(this).parent().parent().find('i').removeClass('icon-collapse-alt icon-expand-alt').addClass('icon-collapse-alt')
    }
});


function getProjectCOSummary(co_id) {
    var JSON_url = '/cpm/changes/tasks/json/' + co_id + '/';
    var task_data = [];
    //var task_list = [];
    $.getJSON(JSON_url, function (data) {
        var list_data = [];
        $.each(data, function (key, value) {
            var list_item = '<li id="task_' + 'id=' + value['id'] + '"><a href="' + value['update_url'] + '">'
                + value['title'] + '</a>'
                + '</li>';

            list_data.push(list_item);
        });
        task_data.push(list_data.join(''));
        $('#task-list').html(task_data.join(''));
    });
}



$('#form-wizard').on('submit', '#project-form', function (event) {
    event.preventDefault();
    var $this = $(this);
    var project_form_title = $this.find('#id_title').val();
    var cookie = 'csrfmiddlewaretoken=' + getCookie('csrftoken') + '&';

    if (project_form_title == "") {
        $this.find("#div_id_title").addClass('error');
        $(project_form_title).after('<span class="help-inline">Title required</span>');
        $(project_form_title).focus();
        return false;
    } else {
        $('.help-inline').remove();
        $("#div_id_title").removeClass('error');
    }
    $.ajax({
        url: project_form_url,
        type: "POST",
        data: cookie + $this.serialize(),
        success: function (data) {
            //console.log(data['form_html']);
            if (!(data['success'])) {
                //console.log('Fail');
                $this.replaceWith(data['form_html']);
            }
            else {
                project_form_url = data['update_url'];
                project_id = data['pk'];
                //console.log('PID:  ' + data['pk']);
                //$('#new-project').find('.success-message').show(1000).hide(5000);
                showStep(2);
                $('#step-nav a[href="#new-category"]').parent().removeClass('disabled');
                $('#step-nav a[href="#new-task"]').parent().removeClass('disabled');
                $('#step-nav a[href="#save"]').parent().removeClass('disabled');
                $('#new-task input#id_title').focus();
            }
        },
        error: function () {
            $('#new-project').find('.error-message').show()
        }
    });
    return false;
});

$('#form-wizard').on('submit', '#task-category-form', function (event) {
    var $this = $(this);
    event.preventDefault();
    var $this_title = $this.find('#id_title').val();
    var this_url;
    var cookie = 'csrfmiddlewaretoken=' + getCookie('csrftoken') + '&';

    if (!$(this).attr('action')) {
        this_url = category_form_url;
    } else {
        this_url = $(this).attr('action');
    }

    $.ajax({
        url: this_url,
        type: "POST",
        data: cookie + $(this).serialize(),
        success: function (data) {
            if (!(data['success'])) {
                $this.replaceWith(data['form_html']);
            }
            else {
                $this.replaceWith(data['form_html']);
                // updates taskform with new category option
                getTaskForm(task_form_url);
                //$this.find('.success-message').show(1000).hide(5000);
                getProjectSummary(project_id);
            }
        },
        error: function () {
            $this.find('.error-message').show();
            alert('error')
        }
    });
    return false;
});

$('#form-wizard').on('submit', '#task-form', function (event) {
    event.preventDefault();
    var $task_form = $(this);
    var task_form_title = $task_form.find('#id_title').val();
    var task_form_category = $task_form.find('#id_category').val();
    var task_form_project = $task_form.find('#id_project');
    var task_url;
    var task_form_changes = '&changes='
    var cookie = 'csrfmiddlewaretoken=' + getCookie('csrftoken') + '&';

    if (task_form_project.val() == "") {
        task_form_project.val(project_id);

    }

    if (!$(this).attr('action')) {
        task_url = task_form_url;
        if (change_order_url_id) {
            task_form_changes += change_order_url_id;
        }
    } else {
        task_url = $(this).attr('action');
    }

    $.ajax({
        url: task_url,
        type: "POST",
        data: cookie + $(this).serialize() + task_form_changes,
        success: function (data) {
            if (!(data['success'])) {
                $task_form.replaceWith(data['form_html']);
            }
            else {
                $task_form.replaceWith(data['form_html']);
                $task_form.find('.success-message').show(1000).hide(5000);
                if ((data['new'])) {
                    $('#ul-category-' + task_form_category).prepend('<li><a href="' + data['update_url'] + '">' + task_form_title + '</a></li>');
                }
                if (!(change_order_url_id)) {
                    getProjectSummary(project_id);
                }
                else {
                    getProjectCOSummary(change_order_url_id);
                }
            }
        },
        error: function () {
            $task_form.find('.error-message').show()
        }
    });
    return false;
});


function editWizardItem(list_id) {
    $(list_id).on('click', 'a', function (event) {
        event.preventDefault();
        var $this = $(this);
        $(list_id + ' *').removeClass('active');

        if ($this.is('[href*="category"]')) {
            showStep(3);
            getTaskCategoryForm($(this).attr('href'));
        }
        else {
            showStep(2);
            getTaskForm($(this).attr('href'));
        }

        $this.parent().addClass('active');
    });

}
editWizardItem('#task-category-list');
editWizardItem('#task-list');
editWizardItem('#project-summary');


function getWizardForm(step, formUrl) {
    $.getJSON(formUrl, function (data) {
        $('#' + step + '-form').replaceWith(data['form_html']);
    });

}

function getProjectForm(projectUrl) {
    $.getJSON(projectUrl, function (data) {
        $('#project-form').replaceWith(data['form_html']);
    });
}
function getTaskForm(taskUrl) {
    $.getJSON(taskUrl, function (data) {
        $('#task-form').replaceWith(data['form_html']);
    });
}
function getTaskCategoryForm(taskUrl) {
    $.getJSON(taskUrl, function (data) {
        $('#task-category-form').replaceWith(data['form_html']);
    });
}


function showStep(step) {
    if (step == 1) {
        $('#step-nav a[href="#new-project"]').tab('show');

    }
    else if (step == 2) {
        $('#step-nav a[href="#new-task"]').tab('show');
    }
    else if (step == 4) {
        $('#step-nav a[href="#save"]').tab('show');
    }
    else {
        $('#step-nav a[href="#new-category"]').tab('show');

    }
}
$('#step-nav a[href="#new-project"]').click(function (e) {
    e.preventDefault();
    if (!($(this).parent().is('.disabled'))) {
        $(this).tab('show');
    }
});
$('#step-nav a[href="#new-category"]').click(function (e) {
    e.preventDefault();
    if (!($(this).parent().is('.disabled'))) {
        $(this).tab('show');
    }
});
$('#step-nav a[href="#new-task"]').click(function (e) {
    e.preventDefault();
    if (!($(this).parent().is('.disabled'))) {
        $(this).tab('show');
    }
});
$('#step-nav a[href="#save"]').click(function (e) {
    e.preventDefault();
    if (!($(this).parent().is('.disabled'))) {
        $(this).tab('show');
    }
});


$('#form-wizard').on('click', '#project-form [name="cancel"]', function (event) {
    event.preventDefault();
    getProjectForm(project_form_url);
    getProjectSummary(project_id);
});

$('#form-wizard').on('click', '#task-form [name="cancel"]', function (event) {
    event.preventDefault();
    getTaskForm(task_form_url);
    getProjectSummary(project_id);
});
$('#form-wizard').on('click', '#task-category-form [name="cancel"]', function (event) {
    event.preventDefault();
    getTaskCategoryForm(category_form_url);
    getProjectSummary(project_id);
});

function deleteWizardItem(deleteUrl) {
    $.ajax({
        url: deleteUrl,
        type: 'POST',
        data: 'csrfmiddlewaretoken=' + getCookie('csrftoken'),
        success: function(data) {
            alert('deleted');
        }
    });
}


$('#form-wizard').on('click', '#task-form [name="delete"]', function (event) {
    event.preventDefault();
    var item_id = $('#task-form').attr('action').split('/').slice(-2)[0];
    var deleteUrl = '/cpm/tasks/delete/' + item_id + '/';
    deleteWizardItem(deleteUrl);
    getWizardForm('task', task_form_url);
    getProjectSummary(project_id);
});
$('#form-wizard').on('click', '#task-category-form [name="delete"]', function (event) {
    event.preventDefault();

    getProjectSummary(project_id);
});

$('#save-project').on('click', function(e) {
    e.preventDefault();
    window.location = '/cpm/images/' + project_id + '/';
});

