import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import mk from './locales/mk.json'

const i18n = createI18n({
  locale: 'mk', // default locale
  fallbackLocale: 'en',
  messages: {
    en,
    mk
  }
})

export default i18n

