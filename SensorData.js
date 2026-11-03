// sensor.js
if (window.DeviceOrientationEvent) {
    window.addEventListener('deviceorientation', function(event) {
        let gamma = Math.round(event.gamma || 0);
        let beta = Math.round(event.beta || 0);
        
        // Send data back to Streamlit
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: { gamma: gamma, beta: beta }
        }, '*');
    }, true);
}

// Listen for device orientation changes
            if (window.DeviceOrientationEvent) {
                window.addEventListener('deviceorientation', function(event) {
                    // gamma: left-to-right tilt (-90 to 90)
                    // beta: front-to-back tilt (-180 to 180)
                    let gamma = Math.round(event.gamma || 0);
                    let beta = Math.round(event.beta || 0);
                    
                    document.getElementById('gamma').innerText = gamma;
                    document.getElementById('beta').innerText = beta;

                    // Streamlit custom component communication bridge
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: { gamma: gamma, beta: beta }
                    }, '*');
                }, true);
            } else {
                document.getElementById('gamma').innerText = "Not Supported";
            }