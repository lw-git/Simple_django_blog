$(document).ready(function () {
	$('#toggle-sidebar').on('click', function(e) {
		$('#sidebar').toggleClass('hidden'); 
      	e.preventDefault();
      	$('#content').toggleClass('col-lg-8 col-lg-12');
	});

	setTimeout(function(){		
		$("#message").fadeOut('slow');
	}, 3000);
});
