// EXPORT OF RAW FOREST CHANGE DATA SPLIT INTO DIFFERENT SHAPEFILES
// Last update: 19.08.2023
// Author: Peter Kamal (peter.kamal@t-online.de)

// This script imports the image collection created in "econ_1_satellite_calculations.js" as "interim".
// Also, it imports a given shapefile as "grid". I run this code for each of the eight shapefiles
// created in the R Notebook "econ_2_shapefile_creation.Rmd". This is to not exceed the memory limit.
// When exporting, make sure the file exports as a GEOJSON to be able to import in R.

// IMPORTS FROM OWN ASSETS (change accordingly)
var interim = ee.ImageCollection("projects/deforestation-sar/assets/bc_intermediate"),
    grid = ee.FeatureCollection("projects/deforestation-sar/assets/thesis_v2/control_one");

// FUNCTIONS FOR LOCAL COMPUTATIONS
// Function that returns the tree cover for a given area
var treecover2000 = function(cell,image){
  var forestSize = image.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: cell.geometry(),
    scale: 30,
    crs: 'EPSG:3005',
    maxPixels: 1e13
  });
  return forestSize.get('treecover2000');
};

// Function that returns the loss in a given year and area
var loss_next = function(cell,image){
  var lossSize = image.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: cell.geometry(),
    scale: 30,
    crs: 'EPSG:3005',
    maxPixels: 1e13
  });
  return lossSize.get('loss');
};

// Function that returns the new tree cover in a given year and area
var treecover_next = function(cell,image){
  var forestSize_next = image.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: cell.geometry(),
    scale: 30,
    crs: 'EPSG:3005',
    maxPixels: 1e13
  });
  return forestSize_next.get('treecover');
};


// Import the intermediate exported result and convert to list
var global_results = interim.toList(interim.size());
//print(global_results);

// Function to perform cell-based reducers and set properties
var local_comp = function(feature){
  var cell = ee.Feature(feature);
  return cell.set('cover2000', treecover2000(cell,ee.Image(global_results.get(1))))
             .set('cover2001', treecover_next(cell,ee.Image(global_results.get(4))))
             .set('cover2002', treecover_next(cell,ee.Image(global_results.get(7))))
             .set('cover2003', treecover_next(cell,ee.Image(global_results.get(10))))
             .set('cover2004', treecover_next(cell,ee.Image(global_results.get(13))))
             .set('cover2005', treecover_next(cell,ee.Image(global_results.get(16))))
             .set('cover2006', treecover_next(cell,ee.Image(global_results.get(19))))
             .set('cover2007', treecover_next(cell,ee.Image(global_results.get(22))))
             .set('cover2008', treecover_next(cell,ee.Image(global_results.get(25))))
             .set('cover2009', treecover_next(cell,ee.Image(global_results.get(28))))
             .set('cover2010', treecover_next(cell,ee.Image(global_results.get(31))))
             .set('cover2011', treecover_next(cell,ee.Image(global_results.get(34))))
             .set('cover2012', treecover_next(cell,ee.Image(global_results.get(37))))
             .set('cover2013', treecover_next(cell,ee.Image(global_results.get(40))))
             .set('cover2014', treecover_next(cell,ee.Image(global_results.get(43))))
             .set('cover2015', treecover_next(cell,ee.Image(global_results.get(46))))
             .set('cover2016', treecover_next(cell,ee.Image(global_results.get(49))))
             .set('cover2017', treecover_next(cell,ee.Image(global_results.get(52))))
             .set('cover2018', treecover_next(cell,ee.Image(global_results.get(55))))
             .set('cover2019', treecover_next(cell,ee.Image(global_results.get(58))))
             .set('cover2020', treecover_next(cell,ee.Image(global_results.get(61))))
             .set('cover2021', treecover_next(cell,ee.Image(global_results.get(64))))
             .set('loss2001', loss_next(cell,ee.Image(global_results.get(3))))
             .set('loss2002', loss_next(cell,ee.Image(global_results.get(6))))
             .set('loss2003', loss_next(cell,ee.Image(global_results.get(9))))
             .set('loss2004', loss_next(cell,ee.Image(global_results.get(12))))
             .set('loss2005', loss_next(cell,ee.Image(global_results.get(15))))
             .set('loss2006', loss_next(cell,ee.Image(global_results.get(18))))
             .set('loss2007', loss_next(cell,ee.Image(global_results.get(21))))
             .set('loss2008', loss_next(cell,ee.Image(global_results.get(24))))
             .set('loss2009', loss_next(cell,ee.Image(global_results.get(27))))
             .set('loss2010', loss_next(cell,ee.Image(global_results.get(30))))
             .set('loss2011', loss_next(cell,ee.Image(global_results.get(33))))
             .set('loss2012', loss_next(cell,ee.Image(global_results.get(36))))
             .set('loss2013', loss_next(cell,ee.Image(global_results.get(39))))
             .set('loss2014', loss_next(cell,ee.Image(global_results.get(42))))
             .set('loss2015', loss_next(cell,ee.Image(global_results.get(45))))
             .set('loss2016', loss_next(cell,ee.Image(global_results.get(48))))
             .set('loss2017', loss_next(cell,ee.Image(global_results.get(51))))
             .set('loss2018', loss_next(cell,ee.Image(global_results.get(54))))
             .set('loss2019', loss_next(cell,ee.Image(global_results.get(57))))
             .set('loss2020', loss_next(cell,ee.Image(global_results.get(60))))
             .set('loss2021', loss_next(cell,ee.Image(global_results.get(63))))
  ;
};


// Map local reducers over feature collection
grid = grid.map(local_comp);

// Export the FeatureCollection to a GEOJSON file.
Export.table.toDrive({
  collection: grid,
  description:'bc_hansen_processed',
  fileFormat: 'GEOJSON'
});
