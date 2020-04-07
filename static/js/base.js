$(document).ready(function () {
	$('#toggle-sidebar').on('click', function(e) {
		$('#sidebar').toggleClass('hidden'); 
      	e.preventDefault();      	
	});

	setTimeout(function(){		
		$(".message").fadeOut('slow');
	}, 5000);
});

