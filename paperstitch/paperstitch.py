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
        paths = [path for path in paths if 'nature' not in path]

    paths = list(set(paths))
    print(f'Found articles: {paths}')
    return paths

def prep(url):
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
        save_folder=url[8:25]
    save_path = f'/home/m/Downloads/{save_folder}/'
    mime_types = "application/pdf,application/vnd.adobe.xfdf,application/vnd.fdf,application/vnd.adobe.xdp+xml"
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)  # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', save_path)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', mime_types)
    profile.set_preference("plugin.disable_full_page_plugin_for_types", mime_types)
    profile.set_preference("pdfjs.disabled", True)
    driver = webdriver.Firefox(profile)
    driver.set_page_load_timeout(8)
    # print('Logging you in to NIH. I give you 20 seconds')
    # driver.get('https://login.ezproxy.nihlibrary.nih.gov/login?url=http://www.nature.com/')
    # time.sleep(20)
    print(f'Saving to {save_path}')
    return driver,save_path,save_folder


def save_journal_issue(url="https://browzine.com/libraries/834/journals/13191/issues/369227236?sort=title"):
    # To prevent download dialog
    driver, save_path, save_folder=prep(url)
    driver.get(url)
    time.sleep(7)
    url=driver.current_url
    driver.set_page_load_timeout(4)
    print(url)
    if ('browzine' in url) or ('nature' in url):
        paths = find_articles(driver, url, pattern='articles/')
        pdf_pattern = '.pdf'
    elif 'sciencemag' in url:
        paths = [url]
        pdf_pattern = 'full.pdf'

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
    driver.close()

def get_fresh_issues():
    save_journal_issue('https://www.nature.com/neuro/current-issue')
    save_journal_issue('https://www.nature.com/nature/current-issue')
    save_journal_issue('https://www.nature.com/nrn/current-issue')
    save_journal_issue('https://www.nature.com/npp/current-issue')
    save_journal_issue('https://www.nature.com/npjschz/current-issue')
    # save_journal_issue('https://www.nature.com/tp/current-issue')
    save_journal_issue('https://science.sciencemag.org/')


if __name__ == '__main__':
    get_fresh_issues()
