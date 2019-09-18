// Disabling eslint rule, following modules are only available in production mode.
/* eslint-disable import/no-unresolved */
const gulp = require('gulp');
const plugins = require('gulp-load-plugins')();
const del = require('del');

/**
 * Disable `arrow-body-style` for readability.
 * WARNING: Gulp `tasks` should always return a `stream` object (https://nodejs.org/api/stream.html).
 */
// eslint-disable-next-line arrow-body-style
gulp.task('less', () => {
  return gulp
    .src('app/styles/main.less')
    .pipe(plugins.plumber())
    .pipe(plugins.less())
    .pipe(plugins.autoprefixer('last 2 version', 'safari 5', 'ie 8', 'ie 9', 'opera 12.1', 'ios 6', 'android 4'))
    .pipe(gulp.dest('app/styles'));
});

gulp.task('clean', () => del(['dist']));

// eslint-disable-next-line arrow-body-style
gulp.task('html', ['clean'], () => {
  return gulp
    .src('app/views/**/*.html')
    .pipe(plugins.plumber())
    .pipe(plugins.htmlmin({ collapseWhitespace: true }))
    .pipe(gulp.dest('dist/views'));
});

// eslint-disable-next-line arrow-body-style
gulp.task('resources', ['clean'], () => {
  return gulp
    .src('app/resources/**/*')
    .pipe(gulp.dest('dist/resources'));
});

// eslint-disable-next-line arrow-body-style
gulp.task('build', ['less', 'html', 'resources'], () => {
  return gulp
    .src('app/index.html')
    .pipe(plugins.plumber())
    .pipe(plugins.useref())
    .pipe(plugins.if('scripts/combined.js', plugins.babel()))
    // Added to prevent leaking informations to an attacker, like packages versions
    .pipe(plugins.if('scripts/dependencies.js', plugins.stripComments()))
    .pipe(plugins.if('scripts/ie.js', plugins.stripComments()))
    .pipe(plugins.if('*.css', plugins.cleanCss()))
    .pipe(gulp.dest('dist'));
});

gulp.task('default', ['build']);
