<?php
session_start();
include("connection.php");
include("functions.php");

if ($_SERVER['REQUEST_METHOD'] == "POST") {
    $email = $_POST['email'];
    $password = $_POST['password'];
    

    if (!empty($email) && !empty($password)) {
        $query = "SELECT * FROM users WHERE email = '$email'";
        $result = mysqli_query($con, $query);

        if ($result && mysqli_num_rows($result) > 0) {
            $user_data = mysqli_fetch_assoc($result);

            if ($user_data['password'] === $password) {
                $_SESSION['email'] = $user_data['email'];
                header("Location: index.php");
                die;
            } else {
                echo "Wrong password.";
            }
        } else {
            echo "User not found.";
        }
    } else {
        echo "Please enter both username and password.";
    }
} 
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta content="IE=edge" http-equiv="X-UA-Compatible">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JuanGPT Log In</title>
    <link rel="icon" href="assets/Logo Blue.png" type="image/x-icon" />
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link
        href="https://fonts.googleapis.com/css2?family=Mochiy+Pop+One&family=Montserrat:ital,wght@0,100..900;1,100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap"
        rel="stylesheet">
    <link rel="stylesheet" href="style.css">
</head>

<body>
    <div class="landing display-fluid">
        <div
            class="account-bg position-absolute top-0 start-0 w-100 h-100 d-flex flex-column justify-content-center align-items-center">
        </div>
        <div class="overlay position-absolute top-0 start-0 w-100 h-100"></div>

        <div class="container d-flex flex-column justify-content-center position-absolute rounded-5 bg-light">
            <div class="row">
                <div class="content col-5 text-light text-center rounded-start-5">
                    <img src="assets/Logo White.png" alt="LOGO" class="title-logo mt-5">
                    <div class="text mx-2">
                        JuanGPT is a conversational AI assistant that allows you to get information and insights about
                        the Demographics and Social Statistics data of the Philippine Statistics Authority.
                    </div>
                </div>

                <div class="account-form col-7 p-5 rounded-end-5 bg-white">
                    <img src="assets/Logo Blue.png" id="bluelogo" class="mx-auto w-20 h-20">
                    <h1 class="text-center fw-bold fs-2">Login</h1>
                    <hr class="hr w-100 my-3 border-top border-warning">

                    <form action="" method="post">
                        <div class="form mb-2 text-dark">
                            <input type="email" required class="form-control form-control-sm shadow-sm" autocomplete="email" id="email" name="email"
                                placeholder="e.g., name@email.com">
                            <label for="email">Email</label>
                        </div>

                        <div class="form mb-2 text-dark">
                            <input type="password" required class="form-control form-control-sm shadow-sm" autocomplete="current-password" id="password" name="password"
                                placeholder="e.g., P@ssw0rd!">
                            <label for="password">Password</label>
                        </div>

                        <button type="submit"
                            class="account-btn px-9 my-4 py-2 btn btn-primary shadow-sm text-white m-auto rounded-pill d-flex justify-content-center align-items-center fw-bold">Log
                            In</button>

                        <div class="account-page d-flex align-items-center justify-content-center pb-4 my-0">
                            <p class="mb-0 me-2 text-center">Don't have an account?</p>
                            <a href="register.php" class="btn btn-outline-primary fw-bold">Register</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function () {
            const sidePanel = document.getElementById('side-panel');
            const mainContent = document.getElementById('main-content');
            const toggleButton = document.getElementById('toggle-button');
            const expandedContent = document.getElementById('expanded-content');
            const label1 = document.getElementsByClassName('label')[0];
            const label2 = document.getElementsByClassName('label')[1];
            let isExpanded = false;

            toggleButton.addEventListener('click', function () {
                isExpanded = !isExpanded;
                if (isExpanded) {
                    sidePanel.classList.remove('col-1');
                    sidePanel.classList.add('col-3');
                    mainContent.classList.remove('col-11');
                    mainContent.classList.add('col-9');
                    expandedContent.classList.remove('d-none');
                    label1.classList.remove('d-none');
                    label1.classList.add('d-block');
                    label2.classList.remove('d-none');
                    label2.classList.add('d-block');

                } else {
                    sidePanel.classList.remove('col-3');
                    sidePanel.classList.add('col-1');
                    mainContent.classList.remove('col-9');
                    mainContent.classList.add('col-11');
                    expandedContent.classList.add('d-none');
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