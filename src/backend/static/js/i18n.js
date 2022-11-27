(() => {
  'use strict'

  document.querySelectorAll('.lang-button').forEach(button => {
    button.addEventListener('click', (event) => {
      changeLang(event.target.dataset.lang);
    });
  })

  const currentLang = window.localStorage.getItem('language') || navigator.language || navigator.userLanguage;
  if (currentLang) changeLang(currentLang.slice(0, 2));

  function changeLang(lang) {
    window.localStorage.setItem('language', lang);

    if (lang === "en") {
      translate(lang, {});
      return
    }

    const url = `${document.location.origin}/static/json/i18n/${lang}.json`;
    fetch(url)
      .then(response => response.json())
      .then(translation => translate(lang, translation))
  }

  function translate(lang, translation) {
    document.querySelectorAll('[data-text]').forEach(elem => {
      const text = elem.dataset.text;
      const trans = translation[text];
      if (trans) {
        elem.textContent = trans;
      } else {
        elem.textContent = text;
        if (lang !== 'en') console.warn(`No translation in "${lang}" for "${text}"`);
      }
    })
  }
})()