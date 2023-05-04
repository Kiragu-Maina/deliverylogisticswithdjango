// toggle night mode
const ball = document.querySelector(".toggle-ball");
const items = document.querySelectorAll(
    ".container,.movie-list-title,.navbar,.navbar-container,.sidebar,.left-menu-icon,.toggle,.toggle-ball"
    );

// const parent = items;

// for (const child of parent.children) {
//       console.log(child);
//     }
ball.addEventListener("click", () => {
   items.forEach(item => {
    console.log(item);
    item.classList.toggle("active")
});
});
// arrow sliders
const arrows = document.querySelectorAll(".arrow");
const movieLists = document.querySelectorAll(".movie-list");

arrows.forEach((arrow,i)=>{
    const itemNumber = movieLists[i].querySelectorAll("img").length;
    let clickCounter = 0;
    arrow.addEventListener("click", () => {
        clickCounter++;
        if(itemNumber - (4 + clickCounter) >= 0){
            movieLists[i].style.transform = `translateX(${
                movieLists[i].computedStyleMap().get('transform')[0].x.value
                -300}px)`;
        } else {
            movieLists[i].style.transform = "translateX(0)";
            clickCounter = 0;
        }
    });
    // console.log(movieLists[i].querySelectorAll("img").length);
});
// profile drop down
const drop = document.querySelector(".dd-list-item");
drop.addEventListener("click", () => {

})

