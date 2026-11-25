const menuButton = document.querySelector(".menu-toggle");
const menuNav = document.querySelector("#menu-nav");

if(menuButton && menuNav){
    function closeMenu(){
        menuNav.classList.remove("is-open");
        menuButton.setAttribute("aria-expanded", "false");
        menuButton.setAttribute("aria-label", "Abrir menu");
    }

    menuButton.addEventListener("click", function (){
        const isOpen = menuButton.getAttribute("aria-expanded") === "true";
        menuNav.classList.toggle("is-open", !isOpen);
        menuButton.setAttribute("aria-expanded", String(!isOpen));
        menuButton.setAttribute(
            "aria-label",
            isOpen ? "Abrir menu" : "Fechar menu"
        );
    });

    //Fechar o menu depois de selecionar o link
    menuNav.querySelectorAll("a").forEach(function(li){
        link.addEventListener("click", closeMenu);
    });

    //Fechar o menu quando pressionar ESC
    document.addEventListener("keydown", function(event){
        if(event.key === "Escape"){
            closeMenu();
        }
    });
}