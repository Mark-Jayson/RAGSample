<?php 
function get_user_data($conn, $email)
{
    $query = "SELECT * FROM users WHERE email = '$email'";
    $result = mysqli_query($conn, $query);

    if ($result && mysqli_num_rows($result) > 0) {
        $user_data = mysqli_fetch_assoc($result);
        return $user_data;
    }

    $_SESSION['error_message'] = "User not found.";
    header("Location: login.php");
    die;
}

function check_login($conn, $email, $password)
{
    if (isset($_SESSION['email'])) {
        $email = $_SESSION['email'];
        $user_data = get_user_data($conn, $email);

        if ($user_data) {
            return $user_data;
        }
    }
    header("Location: login.php");
    die;
}
?>