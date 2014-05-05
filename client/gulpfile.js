var gulp = require('gulp'),
  ngmin = require('gulp-ngmin'),
  autoPrefixer = require('gulp-autoprefixer'),
  minifyCss = require('gulp-minify-css'),
  less = require('gulp-less'),
  jshint = require('gulp-jshint'),
  uglify = require('gulp-uglify'),
  stylish = require('jshint-stylish'),
  filter = require('gulp-filter'),
  clean = require('gulp-clean'),
  htmlmin = require('gulp-htmlmin'),
  useref = require('gulp-useref'),
  karma = require('gulp-karma'),
  protractor = require("gulp-protractor").protractor,
  runSequence = require('gulp-run-sequence'),

  path = require('path');

gulp.task('less', function () {
  return gulp.src('app/styles/main.less')
    .pipe(less({paths: [path.join(__dirname, 'app', 'components', 'bootstrap', 'less')]}))
    .pipe(autoPrefixer('last 2 version', 'safari 5', 'ie 8', 'ie 9', 'opera 12.1', 'ios 6', 'android 4'))
    .pipe(gulp.dest('app/styles'));
});

gulp.task('lint', function() {
  return gulp.src('app/scripts/**/*.js')
    .pipe(jshint())
    .pipe(ngmin())
    .pipe(jshint.reporter('default'));
});

gulp.task('clean', function(){
  return gulp.src(['dist/*'], {read: false})
    .pipe(clean());
});

gulp.task('html', ['clean'], function() {
  return gulp.src('app/views/**/*.html')
    .pipe(htmlmin({collapseWhitespace: true}))
    .pipe(gulp.dest('dist/views'))
});

gulp.task('resources', ['clean'], function() {
  return gulp.src('app/resources/**/*')
    .pipe(gulp.dest('dist/resources'));
});

gulp.task('protractor', [], function () {
  return gulp.src(["test/e2e/*.js"])
    .pipe(protractor({ configFile: "test/protractor-conf.js"}))
    .on('error', function(e) { throw e });
});


gulp.task('karma', [], function () {
  return gulp.src([
      'dist/scripts/dependencies.js',
      'app/components/angular-mocks/angular-mocks.js',
      'dist/scripts/combined.js',
      'test/unit/**/*.js'
    ])
    .pipe(karma({ configFile: 'test/karma.conf.js', action: 'run'}))
    .on('error', function(e) { throw e });
});

gulp.task('build', ['clean', 'less', 'lint'], function () {
  var jsFilter = filter('scripts/combined.js');
  var cssFilter = filter('**/*.css');

  return gulp.src('app/index.html')
    .pipe(useref.assets())
    .pipe(jsFilter)
    .pipe(ngmin())
    .pipe(uglify())
    .pipe(jsFilter.restore())
    .pipe(cssFilter)
    .pipe(minifyCss())
    .pipe(cssFilter.restore())
    .pipe(useref.restore())
    .pipe(useref())
    .pipe(gulp.dest('dist'));
});

gulp.task('default', ['html', 'build']);
gulp.task('dist', ['html', 'resources', 'build']);
gulp.task('full', function(){
  return runSequence('dist', 'karma', 'protractor');
});
