// CALCULATION OF YEARLY FOREST COVER (LOSS) IN BC BETWEEN 2000 and 2021
// Last updated: 19.08.2023
// Author: Peter Kamal (peter.kamal@t-online.de)

// This code calculates yearly forest cover and forest cover loss for the entirety of BC. It exports an image collection with the data to GEE assets.
// The code is a looped and adapted version of this tutorial by Keiko Nomura: https://developers.google.com/earth-engine/tutorials/community/forest-cover-loss-estimation

// IMPORTS: The Hansen GFC data set and a rectangle roughly delineating BC
var hansen = ee.Image("UMD/hansen/global_forest_change_2021_v1_9"),
    geometry = 
    /* color: #d63000 */
    /* displayProperties: [
      {
        "type": "rectangle"
      }
    ] */
    ee.Geometry.Polygon(
        [[[-139.73875294251172, 60.576598327085705],
          [-139.73875294251172, 47.91691994273979],
          [-112.84422169251172, 47.91691994273979],
          [-112.84422169251172, 60.576598327085705]]], null, false);

// SETTING PARAMETERS
// Canopy cover percentage (e.g. 10%) to constitute a forest
var cc = ee.Number(10);

// Minimum forest area in pixels (9 = 0.5ha) to constitute a forest
var pixels = ee.Number(9);

// Minimum mapping area for tree loss (same as the minimum forest area)
var lossPixels = ee.Number(9);

// COMPUTING TREE COVER IN 2000
// Select tree cover in 2000
var canopyCover = hansen.select(['treecover2000']);

// Mask everything below canopy cover
var canopyCover10 = canopyCover.gte(cc).selfMask();

// Use connectedPixelCount() to get contiguous area
var contArea = canopyCover10.connectedPixelCount();

// Apply the minimum area requirement
var minArea = contArea.gte(pixels).selfMask();

// Calculate forest area in hectares
var forestArea = minArea.multiply(ee.Image.pixelArea()).divide(10000);

// COMPUTING TREE LOSS AND NEW FOREST AREA IN SUBSEQUENT YEARS
// Year list to map over
var year_list = ee.List.sequence(1,21);

// List to fill with iterations
var list2000 = ee.List([minArea,ee.Image.constant(0),forestArea]);
var minArea_list = ee.List([list2000]);

//Function to iteratively compute forest loss and cover
var global_iter = function(current,previous){
  // Get the needed parameters from the previous computation
  var previous_minArea = ee.Image(ee.List(ee.List(previous).get(-1)).get(0));
  // Select tree loss band
  var treeLoss = ee.Image(hansen.select(['lossyear']));
  // Select the tree loss in year x and mask everything else
  var treeLoss_year = treeLoss.eq(ee.Image.constant(ee.Number(current))).selfMask();
  // Select the tree loss that fulfils forest requirements
  var treecoverLoss = previous_minArea.and(treeLoss_year)
                                      .rename('loss')
                                      .selfMask();
  // Create connectedPixelCount() to get contiguous area.
  var contLoss = treecoverLoss.connectedPixelCount();
  // Apply the minimum area requirement.
  var minLoss = contLoss.gte(lossPixels).selfMask();
  // Get loss area in hectares
  var lossArea = minLoss.multiply(ee.Image.pixelArea()).divide(10000);
  // Unmask the derived loss.
  var minLossUnmask = minLoss.unmask();
  //Switch the binary value of the loss (0, 1) to (1, 0).
  var notLoss = minLossUnmask.select('loss').eq(0);
  // Combine the derived tree cover and not-loss with 'and'.
  var treecoverLoss_next = previous_minArea.and(notLoss).selfMask();
  // Get contiguous pixels and apply minimum area requirement
  var contArea_next = treecoverLoss_next.connectedPixelCount();
  var minArea_next = contArea_next.gte(pixels);
  // Get updated forest area in hectares
  var forestArea_next = minArea_next.multiply(ee.Image.pixelArea()).divide(10000).rename('treecover');
  
  return ee.List(previous).add(ee.List([minArea_next,lossArea,forestArea_next]));
};

// Run the algorithm
var global_loss_cover = ee.List(year_list.iterate(global_iter,minArea_list));

// Create image collection to be exported as asset
var intermediate_coll = ee.ImageCollection(global_loss_cover.flatten()).map(function(image){
  return image.clip(geometry);
});

var batch = require('users/fitoprincipe/geetools:batch');

var asset = 'bc_intermediate_v2';
var options = {
  name: 'Hansen_{system:index}',
  scale: 30,
  maxPixels: 1e13,
  region: geometry
};

// Uncomment to export
//batch.Download.ImageCollection.toAsset(intermediate_coll, asset, options)

// The image collection is structured in the following way: It contains (for each year):
// The minArea (needed for computation of the subsequent year), the loss area, and the forest cover following the loss. 
// The only image that is missing is the loss in 2000 (which is 0). 
// The types are recognizable by their sizes: minArea ~300Mb, loss ~30Mb, cover ~700Mb.
// If export takes too long, split the years covered into two halves.
