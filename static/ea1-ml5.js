// Initialize the Image Classifier method with MobileNet. A callback needs to be passed.
let classifier;

// A variable to hold the image we want to classify
let img;

function preload() {
  classifier = ml5.imageClassifier('MobileNet');
  img = loadImage('static/images/bird.jpg'); // Pfad zum Bild im static-Ordner
}

function setup() {
  classifier.classify(img, gotResult);
}

// A function to run when we get any errors and the results
function gotResult(error, result) {
  // Display error in the console
  if (error) {
    console.error(error);
  } else {
    // Die Ergebnisse in das div mit der ID "results" einfügen
    $('#result').html(`<p>&nbsp;&nbsp;&nbsp;Label: ${result[0].label}</p>`);
    $('#result').append(`<p>&nbsp;&nbsp;&nbsp;Confidence: ${nf(result[0].confidence, 0, 2)}</p>`);
  }
}
