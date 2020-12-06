"""Main module."""

import inflection
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import os
from tqdm import tqdm
from warnings import warn


def find_articles(driver, url, pattern):
    print(f'Searching {url} for pattern {pattern}')
    try:
        driver.get(url)
    except TimeoutException:
        driver.get(url)
    paths = [paths.get_attribute('href') for paths in driver.find_elements_by_xpath('.//a')]
    paths = [path for path in paths if path is not None]
    paths = [path for path in paths if 'ESM.pdf' not in path]
    paths = [path for path in paths if pattern in path]
    if 'nature' in url:
        # Skip external links from nature websites
        paths = [path for path in paths if 'nature' in path]

    paths = list(set(paths))
    print(f'Found articles: {paths}')
    return paths




def make_save_folder(url):
    if 'browzine' in url:
        driver = webdriver.Firefox()
        driver.get(url)
        time.sleep(2)
        save_folder = driver.title.split('—')[:2]
        save_folder = inflection.underscore(inflection.parameterize(''.join(save_folder)))
        driver.close()
    elif ('nature' in url) and ('current-issue' in url):
        save_folder = f'nature_{url.split("/")[-2]}'
    else:
        save_folder = url[8:25]
    save_path = f'/home/m/Downloads/{save_folder}/'
    return save_path, save_folder


def prep(url=None, use_proxy=False):
    mime_types = "application/pdf,application/vnd.adobe.xfdf,application/vnd.fdf,application/vnd.adobe.xdp+xml"
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)  # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', mime_types)
    profile.set_preference("plugin.disable_full_page_plugin_for_types", mime_types)
    profile.set_preference("pdfjs.disabled", True)
    if url:
        save_path, save_folder = make_save_folder(url)
        profile.set_preference('browser.download.dir', save_path)
    else:
        save_path, save_folder = None, None
    # Make selenium driver
    driver = webdriver.Firefox(profile)
    driver.get("about:config")
    driver.set_page_load_timeout(8)
    if use_proxy:
        # Log in
        print('Logging you in to ezproxy. I give you 20 seconds')
        driver.get('https://login.ezproxy.nihlibrary.nih.gov/login?url=http://www.nature.com/')
        time.sleep(20)
    return driver, save_path, save_folder


def save_journal_issue(url="https://browzine.com/libraries/834/journals/13191/issues/369227236?sort=title",
                       driver=None, save_path=None, save_folder=None):

    def update_save_path(url):
        def set_string_preference(name, value):
            driver.execute_script("""
            var prefs = Components.classes["@mozilla.org/preferences-service;1"]
                .getService(Components.interfaces.nsIPrefBranch);
            prefs.setBoolPref(arguments[0], arguments[1]);
            """, name, value)

        # def set_string_preference(name, value):
        #     modified = driver.execute_script("""
        #         document.getElementById("textbox").value = arguments[0];
        #         FilterPrefs();
        #         view.selection.currentIndex = 0;
        #
        #         if (view.rowCount == 1) {
        #            current_value = view.getCellText(0, {id:"valeuCol"});
        #            if (current_value != arguments[1]) {
        #                ModifySelected();
        #                return true;
        #            }
        #         }
        #
        #         return false;
        #     """, name, value)

            # if modified is None or modified is True:
            #     alert = driver.switch_to.alert
            #     alert.send_keys(value)
            #     alert.accept()

        save_path, save_folder = make_save_folder(url)
        print(f'Saving to {save_path}')
        set_string_preference('browser.download.dir', save_path)
        return save_path, save_folder
    # To prevent download dialog
    if not driver:
        driver, save_path, save_folder = prep(url)
    else:
        save_path, save_folder = update_save_path( url)
    driver.get(url)
    time.sleep(7)
    url = driver.current_url
    driver.set_page_load_timeout(6)
    print(url)
    if ('browzine' in url) or ('nature' in url):
        paths = find_articles(driver, url, pattern='articles/')
        pdf_pattern = '.pdf'
    elif 'sciencemag' in url:
        paths = [url]
        pdf_pattern = 'full.pdf'
    else:
        raise NotImplementedError(f'{url} is not implemented')

    # Download pdfs
    for path in tqdm(paths):
        pdfs = find_articles(driver, path, pattern=pdf_pattern)
        if len(pdfs) > 0:
            for pdf in tqdm(pdfs):
                try:
                    driver.get(pdf)
                except TimeoutException:
                    pass
                except StaleElementReferenceException:
                    warn('You appear to be behind a paywall!')
    print(f'cd {save_path}; pdfunite $(ls -tr *.pdf) ../journals/{save_folder}.pdf')
    os.system(f'cd {save_path}; pdfunite $(ls -tr *.pdf) ../journals/{save_folder}.pdf')
    print(f'Done! use the following command to open with okular: \nokular ~/Downloads/journals/{save_folder}.pdf')
    # driver.close()


def get_fresh_issues():
    save_journal_issue('https://www.nature.com/neuro/current-issue')
    save_journal_issue('https://www.nature.com/nature/current-issue')
    save_journal_issue('https://www.nature.com/nrn/current-issue')
    save_journal_issue('https://www.nature.com/npp/current-issue')
    save_journal_issue('https://www.nature.com/npjschz/current-issue')
    # save_journal_issue('https://www.nature.com/tp/current-issue')
    save_journal_issue('https://science.sciencemag.org/')


def get_fresh_issues_proxy():
    driver, save_path, save_folder = prep(use_proxy=False)
    for url in [
        'https://www.nature.com/neuro/current-issue',
        'https://www-nature-com/nature/current-issue',
        'https://www-nature-com.ezproxy.nihlibrary.nih.gov/neuro/current-issue',
        'https://www-nature-com.ezproxy.nihlibrary.nih.gov/nature/current-issue',
        'https://www-nature-com.ezproxy.nihlibrary.nih.gov/nrn/current-issue',
        'https://www-nature-com.ezproxy.nihlibrary.nih.gov/npp/current-issue',
        'https://www-nature-com.ezproxy.nihlibrary.nih.gov/npjschz/current-issue',
        'https://www-nature-com.ezproxy.nihlibrary.nih.gov/tp/current-issue',
        'https://science-sciencemag-org.ezproxy.nihlibrary.nih.gov/', ]:
        save_journal_issue(url, driver, save_path, save_folder)

    if __name__ == '__main__':
        get_fresh_issues_proxy()
