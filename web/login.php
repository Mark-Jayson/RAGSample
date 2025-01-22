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
    <section class="account-section min-vh-100 position-relative">
        <!-- Background -->
        <div
            class="account-bg position-absolute top-0 start-0 w-100 h-100 d-flex flex-column justify-content-center align-items-center">
        </div>
        <div class="overlay position-absolute top-0 start-0 w-100 h-100"></div>

        <!-- Foreground Content -->
        <div class="container py-5 position-relative z-3">
            <div class="row d-flex justify-content-center align-items-center">
                <div class="col-xl-10 mt-3">
                    <div class="card text-black">
                        <div class="row g-0">

                            <!-- Left Section -->
                            <div class="brand-container col-lg-5 d-flex align-items-center">
                                <div class="text-white px-3 py-4 py-md-5 mx-md-3 text-center">
                                    <img src="assets/Logo White.png" alt="logo">
                                    <p class="medium mb-0">JuanGPT is a conversational AI assistant that
                                        allows you to
                                        get information and insights about
                                        the Demographics and Social Statistics data of the Philippine Statistics
                                        Authority.</p>
                                </div>
                            </div>

                            <!-- Right Section -->
                            <div class="col-lg-7">
                                <div class="card-body py-md-5 mx-md-4">
                                    <div class="text-center">
                                        <h4 class="mt-1 mb-3 pb-1 fw-bold fs-2 text-warning">Login</h4>
                                        <hr class="hr w-100 border-top border-warning">
                                    </div>

                                    <form>
                                        <div class="form mb-2 text-dark">
                                            <input type="email" class="form-control shadow-sm text-black" id="email"
                                                placeholder="name@email.com">
                                            <label for="email">Email</label>
                                        </div>

                                        <div class="form mb-2 text-dark">
                                            <input type="password" class="form-control shadow-sm text-black"
                                                id="password" placeholder="••••••••">
                                            <label for="password">Password</label>
                                        </div>

                                        <button type="submit"
                                            class="account-btn px-9 my-4 py-2 btn btn-primary shadow-sm text-white m-auto rounded-pill d-flex justify-content-center align-items-center fw-bold">
                                            Log In
                                        </button>

                                        <div class="text-center mt-3 text-dark">
                                            <p class="mb-2">Don't have an account? <a href="register.html"
                                                    class="fw-bold">Register</a></p>
                                            <p>Enter as <a href="guest.html" class="fw-bold">Guest</a></p>
                                        </div>
                                    </form>

                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
</body>

</html>