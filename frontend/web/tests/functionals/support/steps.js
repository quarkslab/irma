/* eslint prefer-arrow-callback: "off" */
// See: https://github.com/cucumber/cucumber-js/blob/master/docs/faq.md
/* eslint func-names: "off" */

const { Given, Then, When } = require('cucumber');
const { expect } = require('chai');

const ROOT_URL = 'http://localhost';
const wait = ms => new Promise(r => setTimeout(r, ms));


Given('I am on the main page', async function () {
  // Waiting for networkidle allow XHR to be resolved
  await this.page.goto(ROOT_URL, { waitUntil: 'networkidle0' });
});


Then('I take a screenshot named {string}', async function (name) {
  await this.page.screenshot({ path: name });
});

Then('The page title should be {string}', async function (text) {
  expect(await this.page.title()).to.equal(text);
});

Then('The file {string} should be flagged as a malware', async function (fileName) {
  /**
   * Removing the eslint complaint which would require that the return
   * statement should be at the end of the block scope. Having the `return`
   * statement when the filename is found in the result list is more readable.
   */
  // eslint-disable-next-line consistent-return
  const classNames = await this.page.evaluate(function (selector, name) {
    /**
     * Removing the eslint complaint that `document` is not defined. The
     * `evaluate` function run the code directly in the browser, and `document`
     * is a global variable available there.
     */
    // eslint-disable-next-line no-undef
    const divs = document.querySelectorAll(selector);

    for (let i = 0; i < divs.length; i += 1) {
      if (divs[i].querySelector('a').text === name) {
        return divs[i].querySelector('span').className;
      }
    }
  }, '.infos', fileName);

  expect(classNames).to.include('label-danger');
});

Then('I should see {string} in the search results', async function (fileName) {
  /**
   * Removing the eslint complaint which would require to add a variable to
   * contain the `$x` return value (an `Array`) and pass it to the `expect`
   * function.
   */
  // eslint-disable-next-line no-unused-expressions
  expect(await this.page.$x(`//a[contains(text(), "${fileName}")]`)).not.to.be.empty;
});


When('I wait {int} second(s)', async function (number) {
  await wait(number * 1000);
});

When('I select a malware', async function () {
  await (
    await this.page.$x('//input[@id="file-container"]')
  )[0].uploadFile('/opt/irma/irma-frontend/current/tests/eicar.com');
});

When('I click to choose a file', async function () {
  await (
    await this.page.$x('//button[text()="Choose file")]')
  )[0].click();
});

When('I wait for the upload to finish', async function () {
  await this.page.waitForXPath('//div[@id="scan-infos"]');
});

When('I wait for the scan to finish', async function () {
  await this.page.waitForXPath('//span[text()="Finished"]', { timeout: 10 * 1000 });
});

When('I wait to see a search result', async function () {
  /**
   * Waiting for the search (XHR request) to finish, meaning that the `tbody`
   * should contain (at least) one `tr` element
   */
  await this.page.waitForSelector('#results > table > tbody > tr');
});

When('I type {string} in the search input', async function (search) {
  /**
   * TODO: There is the presence of two `#search` id on the page_ One
   * should be rename or replace with a more specific id.
   */
  await this.page.type('input#search', search);
});

When('I click on {string}', async function (text) {
  /**
   * When using this function, you should add a wait timer or use a
   * step with a `waitFor` function.
   * The function will not wait for the XHR to resolve after clicking on
   * the link and the workaround mentionned there:
   * https://github.com/GoogleChrome/puppeteer/issues/1412#issuecomment-345357063
   * are not working (`timeout after XX miliseconds`)
   */
  const links = await this.page.$x(`//a[contains(text(), "${text}")]`);
  if (links[0] != null) {
    await links[0].click();
    return;
  }

  const buttons = await this.page.$x(`//button[contains(text(), "${text}")]`);
  if (buttons[0] != null) {
    await buttons[0].click();
    return;
  }

  const submits = await this.page.$x(`//input[@type="submit" and contains(@value, "${text}")]`);
  if (submits[0] != null) {
    await submits[0].click();
    return;
  }

  throw Error(`Link "${text}" not found on the page`);
});
