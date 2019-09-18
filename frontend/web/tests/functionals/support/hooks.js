/* eslint prefer-arrow-callback: "off" */
// See: https://github.com/cucumber/cucumber-js/blob/master/docs/faq.md
/* eslint func-names: "off" */

const puppeteer = require('puppeteer');
const {
  After, AfterAll, Before, BeforeAll, setDefaultTimeout, Status,
} = require('cucumber');

const SLOW_MOTION_DELAY = 0; // Slows down Puppeteer operations (in milliseconds)
const HEADLESS = true; // Toggle this value if you want Puppeteer to launch a real browser
const PAGE_WIDTH = 1280;
const PAGE_HEIGHT = 800;
let browser;

setDefaultTimeout(10 * 1000); // Cucumber timeout for steps

BeforeAll(async function () {
  browser = await puppeteer.launch({
    /**
     * Due to Debian kernel version, we need to disable chromium sandbox…
     * See: https://github.com/GoogleChrome/puppeteer/blob/master/docs/troubleshooting.md#chrome-headless-fails-due-to-sandbox-issues
     */
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    headless: HEADLESS,
    slowMo: SLOW_MOTION_DELAY,
  });
});

Before(async function () {
  this.page = this.page || (await browser.pages())[0];
  await this.page.setViewport({ width: PAGE_WIDTH, height: PAGE_HEIGHT });
});

Before({ tags: '@newPage' }, async function () {
  this.page = await browser.newPage();
  await this.page.setViewport({ width: PAGE_WIDTH, height: PAGE_HEIGHT });
});

After(async function (testCase) {
  if (testCase.result.status === Status.FAILED) {
    await this.page.screenshot({ path: 'error.jpeg' });
  }
});

AfterAll(async function () {
  browser.close();
});
