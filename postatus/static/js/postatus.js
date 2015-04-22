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

    function clean(text) {
        text = String(text);
        return text.replace('<', '').replace('>', '').replace('&', '');
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

        // Get the bugs for this locale with the specified summary
        // that changed in the last 28 days. This will pick up new
        // bugs as well as bugs recently resolved.
        //
        // Mike pointed out that we might be better off pulling
        // all the bugs and not limiting by time frame and then
        // showing the top n of them. We can look into that later
        // if 28 doesn't work well enough.
        var params = {
            product: 'Mozilla Localizations',
            component: component,
            short_desc_type: 'allwordssubstr',
            short_desc: project + ': errors in strings',
            f1: 'days_elapsed',
            o1: 'lessthaneq',
            v1: '28',
            query_format: 'advanced'
        };

        fetchBugs(params, function(data, textStatus, jqXHR) {
            console.log(data.bugs);
            if (data.bugs.length > 0) {
                node.append('<p>Existing bugs:</p>');
                node.append('<ul></ul>');
                node = $(node).find('ul');
                $.each(data.bugs, function(index, bug) {
                    node.append('<li>' +
                                '<a href="https://bugzilla.mozilla.org/show_bug.cgi?id=' + clean(bug.id) + '">' +
                                clean(bug.id) + ': ' +
                                clean(bug.summary) + '</a> :: ' +
                                clean(bug.status) + '/' +
                                clean(bug.resolution) + ' :: ' +
                                clean(bug.last_change_time) +
                                '</li>');
                });
            } else {
                node.append('<p>No existing bugs.</p>');
            }
        });
    });

}(jQuery, window));
