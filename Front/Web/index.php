<?php
session_start();
$ch = curl_init();

if (isset($_GET["siguiente"])) {
    if ((int)$_GET["page"] <= $_SESSION["count"]/20) {
        $paginacion = (int)$_GET["page"]+ 1;
    } else {
        $paginacion = (int)$_GET["page"];
    }
} else if (isset($_GET["atras"])) {
    if ((int)$_GET["page"] >= 1) {
        $paginacion = (int)$_GET["page"]- 1;
    } else {
        $paginacion = (int)$_GET["page"];
    }
} else{
    $paginacion = 1;
}
curl_setopt($ch, CURLOPT_URL, "syndael.duckdns.org:8888/modelos?start=" . $paginacion);

curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$res = curl_exec($ch);
curl_close($ch);


$data = json_decode($res, true);
$_SESSION["count"] = $data["count"];
?>

<!doctype html>
<html lang="es">
<head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css"
          integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">

    <title>Synda</title>
</head>
<body>

<div class="container">
    <a href="?start=1"><h1 class="text-center">SYNDAPRINT</h1></a>
    <div>
        <form action="" method="get">
            <input type="hidden" name="page" value="<?= $paginacion ?>">
            <button type="submit" name="siguiente">SIGUIENTE</button>
            <button type="submit" name="atras">ATRAS</button>
        </form>
    </div>
    <div class="card-deck justify-content-center">
        <?php
        $elementoActual = 1;
        $limite = 5;
        if ($data !== false) foreach ($data["items"] as $producto) :
            ?>
            <!--AQUI VA CADA TARJETA DE LA BUSQUEDA-->
            <?php if ($elementoActual === 1) echo "<div class='row'>" ?>
            <div class="card col-4 mb-4">
                <img class="card-img-top img-fluid" src="<?= $producto["img"] ?>" alt="<?= $producto["nombre"] ?>"
                <hr>
                <div class="card-body">
                    <h5 class="card-title"><?= $producto["nombre"] ?></h5>

                </div>
            </div>
            <?php if ($elementoActual === $limite - 1) echo "</div>";
            $elementoActual++;
            if ($elementoActual === $limite) $elementoActual = 1; ?>
        <?php endforeach; ?>
        <?php if ($elementoActual !== 1) echo "</div>"; ?>
    </div>


    <!-- Optional JavaScript -->
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js"
            integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN"
            crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js"
            integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q"
            crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"
            integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl"
            crossorigin="anonymous"></script>
</body>
</html>
