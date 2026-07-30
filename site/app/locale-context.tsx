"use client";

import { createContext, useContext, useState } from "react";

export type Locale = "zh" | "en";
export type Localized = Record<Locale, string>;

type LocaleContextValue = {
  locale: Locale;
  selectLocale: (locale: Locale) => void;
};

const LocaleContext = createContext<LocaleContextValue | null>(null);

export function LocaleProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocale] = useState<Locale>("zh");

  function selectLocale(nextLocale: Locale) {
    setLocale(nextLocale);
    document.documentElement.lang = nextLocale === "zh" ? "zh-CN" : "en";
  }

  return <LocaleContext.Provider value={{ locale, selectLocale }}>{children}</LocaleContext.Provider>;
}

export function useLocale() {
  const value = useContext(LocaleContext);
  if (!value) throw new Error("useLocale must be used within LocaleProvider");
  return value;
}

export function localized(value: Localized, locale: Locale) {
  return value[locale];
}
