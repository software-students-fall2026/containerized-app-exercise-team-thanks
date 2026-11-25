document.addEventListener("DOMContentLoaded", function(){
    const genreSelect= document.getElementById("genre-select");
    const selectedGenre= document.getElementById("selected-genre");

    if(!genreSelect || !selectedGenre){
        return;
    }

    genreSelect.addEventListener("change", function(){

        if (genreSelect.value === ""){
            selectedGenre.textContent= "";
        }
        else{
            selectedGenre.textContent="You selected: " + genreSelect.value;
        }
    });
});