$(document).ready(function() {
    $("#balanced").click(function() {
        var url = $('#balanced-url').val();
        window.location.href = url;
    });
});

$(document).ready(function() {
    $("#classic").click(function() {
        var url = $('#start-url').val();
        window.location.href = url;
    });
});

$(document).ready(function() {
    $("#mode").click(function() {
        var url = $('#mode-url').val();
        window.location.href = url;
    });
});

$(document).ready(function() {
    $("#oracle").click(function() {
        var url = $('#oracle-url').val();
        window.location.href = url;
    });
});

$(document).ready(function() {
    $("#menu").click(function() {
        var url = $('#index-url').val();
        window.location.href = url;
    });
});

$(document).ready(function() {
    $("#custom").click(function() {
        var url = $('#custom-url').val();
        window.location.href = url;
    });
});

$(document).ready(function() {
    $("#custom_oracle").click(function() {
        var url = $('#custom_oracle-url').val();
        window.location.href = url;
    });
});

$(document).ready(function() {
    $("#leaderboard").click(function() {
        var url = $('#leaderboard-url').val();
        window.location.href = url;
    });
});
$(document).ready(function() {
    if (localStorage.getItem('bgColor')) {
        document.body.style.backgroundColor = localStorage.getItem('bgColor');
    }
    if (localStorage.getItem('textColor')){
        document.body.style.color = localStorage.getItem('textColor');
        
        var elements = document.querySelectorAll("h1, h3, h6, p");
        for(var i = 0; i < elements.length; i++) {
            elements[i].style.color = localStorage.getItem('textColor');
        }
    }
    if (localStorage.getItem('bgDaily'))
    {
        var daily = document.getElementById("daily_start");
        daily.style.backgroundColor = localStorage.getItem('bgDaily')
        daily.style.color = localStorage.getItem('colorDaily')   
    }
});

  
function darkMode() {
if (document.body.style.backgroundColor === 'rgb(240, 240, 240)' || document.body.style.backgroundColor === '') {
  document.body.style.backgroundColor = "rgb(1, 62, 102)";
  document.body.style.color = "rgb(240,240,240"

  var elements = document.querySelectorAll("h1, h3, h6, p");
  for(var i = 0; i < elements.length; i++) {
      elements[i].style.color = "rgb(240,240,240)";}
  var daily = document.getElementById("daily_start")
  daily.style.backgroundColor = "rgb(240,240,240)"
  daily.style.color = "rgb(0,0,0)"
}
else{
  document.body.style.backgroundColor = "rgb(240, 240, 240)";
  document.body.style.color = "rgb(0,0,0"

  var elements = document.querySelectorAll("h1, h3, h6, p");
  for(var i = 0; i < elements.length; i++) {
      elements[i].style.color = "rgb(0,0,0)";}

  var daily = document.getElementById("daily_start")
  daily.style.backgroundColor = "rgb(1, 62, 102)"
  daily.style.color = "rgb(240,240,240)"  
}
localStorage.setItem('bgColor', document.body.style.backgroundColor);
localStorage.setItem('textColor', document.body.style.color);
localStorage.setItem('bgDaily', document.getElementById("daily_start").style.backgroundColor)
localStorage.setItem('colorDaily',document.getElementById("daily_start").style.color)
}


