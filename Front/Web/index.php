<?php
session_start();
$ch = curl_init();

if (isset($_GET["buscar"])) {
  $_GET["pagina"] = 1;
}

if (isset($_GET["paginado"])) {
  $paginado = $_GET["paginado"];
} else {
  $paginado = 20;
}

if (isset($_GET["orden"])) {
  $orden = $_GET["orden"];
}

if (isset($_GET["txt_buscar"])) {
  $buscar = $_GET["txt_buscar"];
} else {
  $buscar = null;
}

if (isset($_GET["siguiente"])) {
  if($_GET["pagina"] < ($_SESSION["count"] / $_GET["paginado"])){
    $pagina = $_GET["pagina"] + 1;
  } else {
    $pagina = $_GET["pagina"];
  }
} else if (isset($_GET["atras"])) {
  if(1 < $_GET["pagina"]){
    $pagina = $_GET["pagina"] - 1;
  } else {
    $pagina = $_GET["pagina"];
  }
} else if (isset($_GET["pagina"])){
  if($_GET["pagina"] >= ($_SESSION["count"] / $_GET["paginado"])){
    $_GET["pagina"] = 1;
  }
  $pagina = $_GET["pagina"];
} else {
  $pagina = 1;
}

$url_busqueda = "syn3d.duckdns.org:8888/modelos?";
$url_busqueda = $url_busqueda . "start=" . $pagina;

if($paginado != null){
  $url_busqueda = $url_busqueda . "&limit=" . $paginado;
}
if($buscar != null){
  $url_busqueda = $url_busqueda . "&busca=" . $buscar;
}
if($orden != null){
  $url_busqueda = $url_busqueda . "&orden=" . $orden;
}

curl_setopt($ch, CURLOPT_URL, $url_busqueda);

curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$res = curl_exec($ch);
curl_close($ch);


$data = json_decode($res, true);
$_SESSION["count"] = $data["count"];

$pagina_total = "/" . round($_SESSION["count"] / $paginado + 0.5, 0, PHP_ROUND_HALF_ODD);
$pagina_count = "Registros: " . $_SESSION["count"];
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

    <title>Syndaverse</title>
</head>
<body>

<div class="container">
    <a href="http://syn3d.duckdns.org:9442/"><h1 class="text-center">Syndaverse</h1></a>
    <div>
        <form style="text-align: center;" action="" method="get">
            <input type="text" name="txt_buscar" value="<?= $buscar ?>">
            <button type="submit" name="buscar">Buscar</button>
            <br />
            <button type="submit" name="atras">Atras</button>
            <input style="width: 40px;" onchange="this.form.submit()" type="text" name="pagina" value="<?= $pagina ?>" /><?= $pagina_total ?>
            <button type="submit" name="siguiente">Siguiente</button>
            <?= $pagina_count ?>

            <select name="paginado" onchange="this.form.submit()">
              <option <?php echo $paginado == '5' ? 'selected' : ''?>>5</option>
              <option <?php echo $paginado == '10' ? 'selected' : ''?>>10</option>
              <option <?php echo $paginado == '20' ? 'selected' : ''?>>20</option>
              <option <?php echo $paginado == '50' ? 'selected' : ''?>>50</option>
            </select>

            <select name="orden" onchange="this.form.submit()">
              <option value="fecha_ins" <?php echo $orden == 'fecha_ins' ? 'selected' : ''?>>Reciente</option>
              <option value="nombre" <?php echo $orden == 'nombre' ? 'selected' : ''?>>Nombre</option>
            </select>
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
