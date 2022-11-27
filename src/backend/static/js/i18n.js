(() => {
  'use strict'

  document.querySelectorAll('.lang-button').forEach(button => {
    button.addEventListener('click', changeLang);
  })

  let currentLang = window.localStorage.getItem('language');
  if (currentLang) changeLang(currentLang);

  function changeLang(event) {
    let lang;

    if (event.target) {
      lang = event.target.dataset.langId;
    } else {
      lang = "en";
    }

    window.localStorage.setItem('language', lang);

    if (lang === "en") {
      translate(lang, {})
      return
    }

    const url = `${document.location.origin}/static/json/i18n/${lang}.json`;
    fetch(url)
      .then(response => response.json())
      .then(translation => translate(lang, translation))
  }

  function translate(lang, translation) {
    document.querySelectorAll('[data-lang]').forEach(elem => {
      const text = elem.dataset.lang;
      const trans = translation[text];
      if (trans) {
        elem.textContent = trans;
      } else {
        elem.textContent = text;
        console.warn(`No translation in ${lang} for "${text}"`);
      }
    })
  }
})()