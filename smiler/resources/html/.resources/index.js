(function () {
    redbars = document.querySelectorAll('img.redbar')
    greenbars = document.querySelectorAll('img.greenbar')

    maxBarWidth(redbars, greenbars)
    
})()

function maxBarWidth(redbars, greenbars) {
    var max = 120;
    var newmax = 120;
    for (i = 0; i < redbars.length; i++) {
        newmax = redbars[i].width + greenbars[i].width;
        if (newmax > max) {
            max = newmax;
        }
    }
    var maxWidth = 120;
    for (i = 0; i < redbars.length; i++) {
        red_width = redbars[i].width / max * maxWidth;
        green_width = greenbars[i].width / max * maxWidth;
        redbars[i].width = redbars[i].width > 0 && red_width < 1 ? 1 : red_width;
        greenbars[i].width = greenbars[i].width > 0 && green_width < 1 ? 1 : green_width;
        if (newmax > max) {
            max = newmax;
        }
    }

    return max
}