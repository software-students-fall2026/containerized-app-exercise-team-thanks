document.addEventListener("DOMContentLoaded", () => {
    const audio =document.getElementById("audio-player");
    const playButton=document.getElementById("play-pause-btn");
    
    if(!audio || !playButton){
        return;
    }

    playButton.addEventListener("click", function(){
        if(audio.paused){
            audio.play();

        }
        else{
            audio.pause();
        }

    });

    audio.addEventListener("play", function(){
        playButton.textContent = "Pause";
    });

    audio.addEventListener("pause", function(){
        playButton.textContent = "Play";
    });

    audio.addEventListener("ended", function(){
        playButton.textContent = "Play";
    });

});