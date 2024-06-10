(function () {
    redbars = document.querySelectorAll('img.redbar')
    greenbars = document.querySelectorAll('img.greenbar')

    maxBarWidth(redbars, greenbars)
    
})()

function maxBarWidth(redbars, greenbars) {
    let width = (elem) => parseInt(elem.alt)
    let red_widths = Array.from(redbars).map(width)
    let green_widths = Array.from(greenbars).map(width)
    let max = Math.max.apply(Math,red_widths.map((x, i) => green_widths[i] + x))
    let maxWidth = 120;
    for (i = 0; i < redbars.length; i++) {
        red_w = red_widths[i] / max * maxWidth
        green_w = green_widths[i] / max * maxWidth
        redbars[i].width = red_widths[i] > 0 && red_w < 1 ? 1 : red_w;
        greenbars[i].width = green_widths[i] > 0 && green_w < 1 ? 1 : green_w;

    }
}