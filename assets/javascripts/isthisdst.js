$(function() {

    var findLocation = function(position) {
        $.cookie( 'native_lat', position.coords.latitude, 1 );
        $.cookie( 'native_lng', position.coords.longitude, 1 );

        window.location.replace("/location/lat/" + $.cookie( 'native_lat' ) + "/lng/" + $.cookie( 'native_lng' ));
    }


    var handleError = function( error ) {
        $.cookie( 'location_error', 'true', 1 );
        $.cookie( 'location_error_reason', error.code, 1 );
    }


    if( Modernizr.touch ) {
        if( ( !$.cookie( 'native_lat' ) || !$.cookie( 'native_lng' ) ) && !$.cookie('location_error') ){
            if( navigator.geolocation ) {
                navigator.geolocation.getCurrentPosition( findLocation, handleError, {timeout:10000} );
            }
        }
    }

});