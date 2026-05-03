

function fill_div_part(div_id, path, parameters = {}) {
    var div_part = document.getElementById(div_id);

    console.log("Filling DIV Part: " + div_id + ', path: ' + path + ', paramters: ' + JSON.stringify(parameters));
    return $.ajax({
        type: "get",
        url: path,
        data: parameters,
        success: function(response) {
            console.log("Success DIV Part: " + div_id + ', path: ' + path + ', paramters: ' + JSON.stringify(parameters));
            div_part.innerHTML = response;

            //reload_css_functions();
        },
        error: function(response) {
            console.log("FAILURE DIV Part: " + div_id + ', path: ' + path + ', paramters: ' + JSON.stringify(parameters) + ', error: ' + response.status);
            alert("Failed to fill screen parts. Check console log for more info.");
        }
    });

}

function reload_css_functions() {
        // Wire the icon search
    $('#icon-search-input').on('input', function() {
        var searchStr = $('#icon-search-input').val();
        if (searchStr !== '') {
            setIcons(searchIcons(searchStr));
        }
        else {
            clearSearch();
        }
    });

    // Wire the global search
    $('#search-kit').on('click', function() {
        if ($('#search-kit').val() === '') {
            doGlobalSearch('', true);
        }
    });
    $('#search-kit').on('input', function() {
        doGlobalSearch($('#search-kit').val(), false);
    });

    // Wire the gauge reset button
    $('#gauge-start').click(function() {
        if (curGaugeTimer) { clearTimeout(curGaugeTimer); }
        curGaugeProgress = 0;
        startGaugeAnimation();
    });

    // Wire the progressbar reset button
    $('#progressbar-start').click(function() {
        if (curProgressTimer) { clearTimeout(curProgressTimer); }
        curProgress = 0;
        startProgressAnimation();
    });

    // Wire the header sidebar toggle button
    $('#sidebar-toggle').click(function() {
        $('#styleguideSidebar').toggleClass('sidebar--mini');
        $('#sidebar-toggle span:first-child').removeClass();
        if ($('#styleguideSidebar').hasClass('sidebar--mini')) {
            $('#sidebar-toggle span:first-child').addClass('icon-list-menu');
        } else {
            $('#sidebar-toggle span:first-child').addClass('icon-toggle-menu');
        }
    });

    $('#mobile-sidebar-toggle').click(function() {
        $('#styleguideSidebar').removeClass('sidebar--mini');
        $('#styleguideSidebar').toggleClass('sidebar--hidden');
    });

    // Wire the sidebar drawer open/close toggles
    $('#styleguideSidebar .sidebar__drawer > a').click(function(e) {
        e.stopPropagation();
        $(this).parent().siblings().removeClass('sidebar__drawer--opened');
        $(this).parent().toggleClass('sidebar__drawer--opened');
    });

    // Wire the sidebar selected item
    $('#styleguideSidebar .sidebar__item > a').click(function() {
        $('#styleguideSidebar .sidebar__item').removeClass('sidebar__item--selected');
        $(this).parent().addClass('sidebar__item--selected');
    });

    // Wire the sidebar examples
    $('body .sidebar__drawer > a').click(function() {
        $(this).parent().toggleClass('sidebar__drawer--opened');
    });
    $('body .sidebar__item > a').click(function() {
        $(this).parent().siblings().removeClass('sidebar__item--selected');
        $(this).parent().addClass('sidebar__item--selected');
    });

    // Wire the button group examples
    $('body .btn-group .btn').click(function() {
        $(this).siblings().removeClass('selected');
        $(this).addClass('selected');
    });

    // Wire the markup toggles
    $('body .markup').removeClass('active');
    $('body .markup-toggle').click(function() {
        $(this).parent().next().toggleClass('hide');
        $(this).parent().toggleClass('active');

        if ($(this).hasClass('active')) {
            $(this).find('.markup-label').text('Hide code');
        }
        else if (!$(this).hasClass('active')) {
            $(this).find('.markup-label').text('View code');
        }
    });

    // Wire the markup copy to clipboard events
    $('body .clipboard-toggle').click(function() {
        clipboard.copy($(this).parent().parent().find('code.code-raw').text());
        showToast('Copied code to clipboard');
        $(this).addClass('text-bold').text('copied!');
    });

    copyIconToClipboard('icon-main-results');

    // Wire the tabs
    $('body li.tab').click(function() {
        doTabChange(this.id);
        //$(this).siblings().removeClass('active');
        //var tabsId = this.id.substring(0, this.id.indexOf('-'));
        //$('body #'+tabsId+'-content > .tab-pane').removeClass('active');
        //$(this).addClass('active');
        //$('body #'+this.id+'-content').addClass('active');
    });

    // Wire pagination
    $('body ul.pagination > li > a').click(function() {
        var el = $(this).parent().siblings().find('.active');
        $(this).parent().siblings().removeClass('active');
        $(this).parent().addClass('active');
    });

    // Wire closeable alerts
    $('body .alert .alert__close').click(function() {
        $(this).parent().addClass('hide');
    });

    // Wire the Card pattern examples
    $('body a.panel').click(function() {
        $(this).toggleClass('selected');
    });

    // Wire the Advanced Grid example
    $('body #grid-group').click(function() {
        $(this).parent().find('#grid-group').removeClass('selected');
        var cls = 'grid--' + $(this).text();
        $('body .grid').removeClass('grid--3up');
        $('body .grid').removeClass('grid--4up');
        $('body .grid').removeClass('grid--5up');
        $('body .grid').addClass(cls);
        $(this).addClass('selected');
    });

    $('body #grid-cards').change(function() {
        addCards($(this).val());
    });

    $('body #grid-gutters').change(function() {
        $('body #grid').css('gridGap', $(this).val()+'px');
    });

    $('body #grid-selectable').change(function() {
        $('body #grid').toggleClass('grid--selectable');
        $('body .grid .panel').removeClass('selected');
    });

    addCards(15);

    // Wire the carousel examples
    $('body .carousel__controls a.dot').click(function() {
        setActiveSlide(this, 'fadeIn');
    });
    $('body .carousel__controls a.back').click(function() {
        var last = $(this).parent().find('a.dot').last();
        var cur = $(this).parent().find('a.dot.active');
        var active = cur.prev();
        if (active[0].id === "") {
            active = last;
        }
        setActiveSlide(active[0], 'slideInLeftSmall');
    });
    $('body .carousel__controls a.next').click(function() {
        var first = $(this).parent().find('a.dot').first();
        var cur = $(this).parent().find('a.dot.active');
        var active = cur.next();
        if (active[0].id === "") {
            active = first;
        }
        setActiveSlide(active[0], 'slideInRightSmall');
    });

    wireHomeNav();

    // Wire the accordion examples
    wireAccordion();

    // Wire scroll to top button
    wireScrollToTop();

    // Wire the dropdown examples
    $('body .dropdown').not('.ignore').click(function(e) {
        e.stopPropagation();
        var el = $(this).find('input');
        if (!el.hasClass('disabled') && !el.attr('disabled') && !el.hasClass('readonly') && !el.attr('readonly')) {
            $(this).toggleClass('active');
        }
    });
    $('body .dropdown:not(.ignore) .dropdown__menu a').click(function(e) {
        e.stopPropagation();

        var origVal = $(this).parent().parent().find('input').val();
        var newVal = $(this).text();

        $(this).parent().find('a').removeClass('selected');
        $(this).addClass('selected');
        $(this).parent().parent().find('input').val($(this).text());
        $(this).parent().parent().removeClass('active');

        var id = $(this).parent().parent()[0].id;
        if (id === 'themeSwitcher') {
            switchTheme($(this).text());
        }
    });

    // Close dropdowns and open sidebar drawers on clicks outside the dropdowns
    $(document).click(function() {
        $('body .dropdown').not('.ignore').removeClass('active');
        $('#styleguideSidebar .sidebar__drawer').removeClass('sidebar__drawer--opened');
    });

    // Wire the selectable tables
    $('body .table.table--selectable tbody > tr').click(function() {
        $(this).toggleClass('active');
        var cb = $(this).find('td .checkbox input');
        if (cb) {
            cb.prop('checked', !cb.prop('checked'));
        }
    });
    // Wire the table wells example
    $('body #table-wells tbody > tr').click(function() {
        $(this).find('td span.icon-chevron-up').removeClass('icon-chevron-up').addClass('icon-chevron-down');
        $(this).find('td span.icon-chevron-down').removeClass('icon-chevron-down').addClass('icon-chevron-up');
        $(this).next().toggleClass('hide');
    });

    // Wire the global modifiers
    $('body #global-animation').change(function() {
        $('body').toggleClass('cui--animated');
    });
    $('body #global-headermargins').change(function() {
        $('body').toggleClass('cui--headermargins');
    });
    $('body #global-spacing').change(function() {
        $('body').toggleClass('cui--compressed');
    });
    $('body #global-wide').change(function() {
        $('body').toggleClass('cui--wide');
    });
    $('body #global-sticky').change(function() {
        $('body').toggleClass('cui--sticky');
    });

    // Load the changelog
    //$.get('changelog.md', function(markdownContent) {
    //    var converter = new Markdown.Converter();
    //    $("#changelog-content").html(converter.makeHtml(markdownContent));
    //});

    // Load the broadcast file (if it exists)
    //$.getJSON('broadcast.json', function(data) {
    //    if (data && data.text && data.text.length) {
    //        $("#broadcast-msg").html(data.text);
    //        $("#broadcast").toggleClass('hide');
    //    }
    //});

    window.addEventListener('hashchange', function (e) {
        checkUrlAndSetupPage(e.newURL);
    }, false);

    // Check for anchor link in the URL
    checkUrlAndSetupPage(window.location.href);

    // Listen of window changes and close the sidebar if necessary
    $(window).resize(function() {
        shouldHideSidebar();
    });

    shouldHideSidebar();
    populateSearchIcons();
    populateSearchEntries();
    populateSwatches();
    checkTheme();
}