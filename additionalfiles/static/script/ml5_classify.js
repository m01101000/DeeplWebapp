let classifier;
let img;
                
function preload() {
    classifier = ml5.imageClassifier('MobileNet');
    img = loadImage("{{ url_for('static', filename='uploads/'+ username + '/' + user_file_name) }}");
}
              
function setup() {
    createCanvas(400, 400);
    classifier.classify(img, gotResult);
    let imgElement = createImg(img.src); // Create img element
    imgElement.parent('img'); // Append img element to 'img' div
}
                
function gotResult(error, results) {
    if (error) {
        console.error(error);
    }
    console.log(results);
    let resultDiv = createDiv(`Label: ${results[0].label}<br><br>`); // Create div for label
    resultDiv.parent('classification_result'); // Append div to 'results' div
    let confidenceDiv = createDiv(`Confidence: ${nf(results[0].confidence, 0, 2)}`); // Create div for confidence
    confidenceDiv.parent('classification_result'); // Append div to 'results' div
}