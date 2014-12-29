(function($, window) {
    'use strict';

    var BUGZILLA_URL = 'https://bugzilla.mozilla.org/rest/';

    // http://stackoverflow.com/a/1714899/205832
    // From buggy.
    function serializeObject(obj) {
        var str = [];
        var key;

        for (key in obj) {
            if (obj.hasOwnProperty(key)) {
                var val = obj[key];
                if (val instanceof Array) {
                    $.each(val, function(index, part) {
                        str.push(encodeURIComponent(key) + '=' + encodeURIComponent(part));
                    });
                } else {
                    str.push(encodeURIComponent(key) + '=' + encodeURIComponent(val));
                }
            }
        }
        return str.join("&");
    }

    function fetchBugs(params, callback) {
        var url = BUGZILLA_URL + 'bug';
        url += '?' + serializeObject(params);

        $.ajax({
            url: url,
            success: callback,
            dataType: 'json'
        });
    }

    var project = $('h1#project').data('name');
    var l10nComponents = $('h1#project').data('components');

    $.each($('.locale'), function(index, value) {
        var name = $(value).data('name');
        var component = l10nComponents[name.replace('_', '-')];
        var node = $(value).find('.buglist');

        var params = {
            product: 'Mozilla Localizations',
            component: component,
            bug_status: ['UNCONFIRMED', 'NEW', 'ASSIGNED'],
            short_desc_type: 'allwordssubstr',
            short_desc: project + ': errors in strings'
        };

        fetchBugs(params, function(data, textStatus, jqXHR) {
            console.log(data.bugs);
            if (data.bugs.length > 0) {
                node.append('<p>Existing bugs:</p>');
                node.append('<ul></ul>');
                node = $(node).find('ul');
                $.each(data.bugs, function(index, bug) {
                    console.log(bug);
                    var id = bug.id;
                    var summary = bug.summary;
                    // FIXME: This is goofy.
                    summary = summary.replace('<', '').replace('>', '');
                    node.append('<li><a href="https://bugzilla.mozilla.org/show_bug.cgi?id=' + id + '">' + id + ': ' + summary + '</a></li>');
                });
            } else {
                node.append('<p>No existing bugs.</p>');
            }
        });
    });

}(jQuery, window));
