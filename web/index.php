<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JuanGPT</title>
    <link rel="icon" type="image/x-icon" href="Midterms 1 - Unit 4 Video/MJA logo@4x-8.png">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=K2D:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,500;1,600;1,700;1,800&display=swap"
        rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</head>

<body>
    
        <button id="toggle-button" class="toggle-button btn btn-link text-white">
            <i class="fas fa-bars"></i>
        </button>
        <div id="side-panel"
            class="position-fixed top-0 start-0 h-100 bg-dark text-white transition-all duration-300 z-50">
            <!-- <button id="toggle-button" class="btn btn-link text-white p-4">
                <i class="fas fa-bars"></i>
            </button> -->

            <div id="expanded-content" class=" p-3 d-none">
                <button class="btn btn-link text-white p-2">
                    <i class="fas fa-plus"></i> New Chat
                </button>
 
                <h2 class="text-lg font-semibold mb-2">Recent</h2>
                <div class="text-gray-200">Recent chats will appear here</div>
                <div class="text-gray-200">Recent chats will appear here</div>
                <div class="text-gray-200">Recent chats will appear here</div>
            </div>

            <div class="position-absolute bottom-0 start-0 w-100 p-3">
                <button class="btn btn-link text-white">
                    <row><i class="fas fa-info-circle"></i><label class="label d-none">JuanGPT</label></row>
                </button><br>
                <button class="btn btn-link text-white">
                    <i class="fas fa-cog"></i> <label class="label d-none">Settings</label>
                </button>
            </div>
        </div>
        

        <div id="main-content"
            class="main-content position-fixed top-0 end-0 h-100 bg-dark text-white transition-all duration-300 z-50">
            
            <nav class="navbar navbar-light">
                <!-- <button id="smallbutton" class="btn btn-link text-white">
                    <i class="fas fa-bars"></i>
                </button> -->
                <a class="navbar-brand" href="#">
                    <img src="assets/Logo White.png" alt="LOGO" class="logo d-flex justify-content-start">
                </a>
                <div class="d-flex justify-content-end align-items-center gap-2">
                    <a href="login.html" class="btn btn-warning rounded-5">Log In</a> <br>
                    <a href="signup.html" class="btn log btn-outline-warning rounded-5">Sign Up</a>
                </div>
            </nav>
            

            <banner>
                <div class="position-relative image-container"
                    style="background: linear-gradient(to right, black, transparent);">
                    <div class="image-section" style="background-image: url('assets/1.jpg');"></div>
                    <div class="image-section" style="background-image: url('assets/2.jpg');"></div>
                    <div class="image-section" style="background-image: url('assets/3.jpg');"></div>

                    <div class="position-absolute top-0 start-0 w-100 h-100">
                        <div class="banner-text display-5 position-absolute"
                            style="z-index: 1; color: white; width: 50vw;">
                            Discover the condition of the Filipino people thru Data</div>
                        <div class="w-100 h-100"
                            style="background: linear-gradient(to right, rgba(0,0,0,0.8), rgba(0,0,0,0));">
                        </div>
                    </div>
                </div>
            </banner>

            <main>
                <!-- User Input -->
                <div class="input-group mb-3"> 
                    <input type="text" class="control" placeholder="Message JUANGPT" aria-label="Message JUANGPT"
                        aria-describedby="button-addon2">
                    <button class="btn btn-light" type="button" id="button-addon2">
                        <img src="assets/Paper Plane.png" width="30" height="30">
                    </button>
                </div>
            </main>
        </div>
    

    <script>
        document.addEventListener('DOMContentLoaded', function () {
            const sidePanel = document.getElementById('side-panel');
            const mainContent = document.getElementById('main-content');
            const toggleButton = document.getElementById('toggle-button');
            const expandedContent = document.getElementById('expanded-content');
            const label1 = document.getElementsByClassName('label')[0];
            const label2 = document.getElementsByClassName('label')[1];
            const smallbutton = document.getElementById('smallbutton');
            let isExpanded = false;
             
toggleButton.addEventListener('click', function () {
    isExpanded = !isExpanded;
    if (window.innerWidth <= 576) {
        if (isExpanded) {
       
                    sidePanel.style.width = '100vw';
                    sidePanel.style.display = 'block';
                    mainContent.style.display = 'none';
                    expandedContent.classList.remove('d-none');
                    label1.classList.remove('d-none');
                    label1.classList.add('d-block');
                    label2.classList.remove('d-none');
                    label2.classList.add('d-block');

        } else {
            sidePanel.style.display = 'none';
                    mainContent.style.display = 'block';
                    mainContent.style.width = '100vw';
                    sidePanel.style.width = 'none';
        }
        
       
    } else {
        if (isExpanded) {
            sidePanel.style.width = '25vw';
                    // sidePanel.classList.add('col-3');
                    mainContent.style.width = '75vw';
                    
                    expandedContent.classList.remove('d-none');
                    label1.classList.remove('d-none');
                    label1.classList.add('d-block');
                    label2.classList.remove('d-none');
                    label2.classList.add('d-block');
       
       
   } else {
                    sidePanel.style.width = '5vw';
                    mainContent.style.width = '95vw';
                    expandedContent.classList.add('d-none');
                    label1.classList.add('d-none');
                    label1.classList.remove('d-block');
                    label2.classList.add('d-none');
                    label2.classList.remove('d-block'); 
   }
    }
});

window.addEventListener('resize', function() {
    const sidePanel = document.getElementById('side-panel');
    const mainContent = document.getElementById('main-content');
    
    if (window.innerWidth <= 576) { 
        sidePanel.style.display = 'none';
        mainContent.style.display = 'block';
        mainContent.style.width = '100vw';
        sidePanel.style.width = 'none';
    } 
    else {
        sidePanel.style.width = '5vw';
                    mainContent.style.width = '95vw';
                    mainContent.style.display = 'block';
                    expandedContent.classList.add('d-none');
                    sidePanel.style.display = 'block';
                    label1.classList.add('d-none');
                    label1.classList.remove('d-block');
                    label2.classList.add('d-none');
                    label2.classList.remove('d-block'); 
        
        
    }
});
            
        });
    </script>
</body>

</html>