import { create } from "zustand";
import { persist } from "zustand/middleware";

/**
 * Theme configuration types
 */
export type ThemeName = "ocean" | "sunset" | "forest" | "monochrome" | "system";

export interface ThemeColors {
  primary: string;
  primaryForeground: string;
  secondary: string;
  secondaryForeground: string;
  accent: string;
  accentForeground: string;
  muted: string;
  mutedForeground: string;
}

export interface ThemeConfig {
  name: ThemeName;
  displayName: string;
  light: ThemeColors;
  dark: ThemeColors;
}

/**
 * Predefined theme palettes
 */
export const themes: Record<ThemeName, ThemeConfig> = {
  ocean: {
    name: "ocean",
    displayName: "Ocean",
    light: {
      primary: "201 96% 32%", // Blue
      primaryForeground: "0 0% 100%",
      secondary: "186 100% 35%", // Teal
      secondaryForeground: "0 0% 100%",
      accent: "199 95% 74%",
      accentForeground: "201 96% 9%",
      muted: "198 16% 84%",
      mutedForeground: "201 13% 28%",
    },
    dark: {
      primary: "201 96% 32%",
      primaryForeground: "0 0% 100%",
      secondary: "186 100% 35%",
      secondaryForeground: "0 0% 100%",
      accent: "199 95% 25%",
      accentForeground: "0 0% 100%",
      muted: "201 24% 16%",
      mutedForeground: "198 16% 84%",
    },
  },
  sunset: {
    name: "sunset",
    displayName: "Sunset",
    light: {
      primary: "24 100% 50%", // Orange
      primaryForeground: "0 0% 100%",
      secondary: "346 83% 47%", // Pink
      secondaryForeground: "0 0% 100%",
      accent: "24 100% 90%",
      accentForeground: "24 100% 10%",
      muted: "24 20% 90%",
      mutedForeground: "24 10% 40%",
    },
    dark: {
      primary: "24 100% 50%",
      primaryForeground: "0 0% 100%",
      secondary: "346 83% 47%",
      secondaryForeground: "0 0% 100%",
      accent: "24 100% 20%",
      accentForeground: "0 0% 100%",
      muted: "24 20% 15%",
      mutedForeground: "24 20% 90%",
    },
  },
  forest: {
    name: "forest",
    displayName: "Forest",
    light: {
      primary: "142 71% 45%", // Green
      primaryForeground: "0 0% 100%",
      secondary: "88 50% 53%", // Lime
      secondaryForeground: "0 0% 0%",
      accent: "142 71% 85%",
      accentForeground: "142 71% 15%",
      muted: "142 15% 85%",
      mutedForeground: "142 15% 35%",
    },
    dark: {
      primary: "142 71% 45%",
      primaryForeground: "0 0% 100%",
      secondary: "88 50% 53%",
      secondaryForeground: "0 0% 0%",
      accent: "142 71% 20%",
      accentForeground: "0 0% 100%",
      muted: "142 20% 15%",
      mutedForeground: "142 15% 85%",
    },
  },
  monochrome: {
    name: "monochrome",
    displayName: "Monochrome",
    light: {
      primary: "0 0% 9%", // Black
      primaryForeground: "0 0% 98%",
      secondary: "0 0% 45%", // Gray
      secondaryForeground: "0 0% 98%",
      accent: "0 0% 96%",
      accentForeground: "0 0% 9%",
      muted: "0 0% 96%",
      mutedForeground: "0 0% 45%",
    },
    dark: {
      primary: "0 0% 98%",
      primaryForeground: "0 0% 9%",
      secondary: "0 0% 63%",
      secondaryForeground: "0 0% 9%",
      accent: "0 0% 15%",
      accentForeground: "0 0% 98%",
      muted: "0 0% 15%",
      mutedForeground: "0 0% 63%",
    },
  },
  system: {
    name: "system",
    displayName: "System",
    light: {
      primary: "222 47% 11%",
      primaryForeground: "210 40% 98%",
      secondary: "210 40% 96%",
      secondaryForeground: "222 47% 11%",
      accent: "210 40% 96%",
      accentForeground: "222 47% 11%",
      muted: "210 40% 96%",
      mutedForeground: "215 16% 47%",
    },
    dark: {
      primary: "210 40% 98%",
      primaryForeground: "222 47% 11%",
      secondary: "217 33% 17%",
      secondaryForeground: "210 40% 98%",
      accent: "217 33% 17%",
      accentForeground: "210 40% 98%",
      muted: "217 33% 17%",
      mutedForeground: "215 20% 65%",
    },
  },
};

/**
 * Theme store state interface
 */
interface ThemeState {
  theme: ThemeName;
  accentColor: string;
  darkMode: boolean;
  animations: boolean;

  setTheme: (theme: ThemeName) => void;
  setAccentColor: (color: string) => void;
  toggleDarkMode: () => void;
  setDarkMode: (enabled: boolean) => void;
  toggleAnimations: () => void;
  applyTheme: () => void;
}

/**
 * Theme store with Zustand
 * Persists to localStorage and syncs with backend preferences
 */
export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: "system",
      accentColor: "#3b82f6",
      darkMode: false,
      animations: true,

      setTheme: (theme) => {
        set({ theme });
        get().applyTheme();
      },

      setAccentColor: (color) => {
        set({ accentColor: color });
        // Apply custom accent color to CSS variables
        document.documentElement.style.setProperty("--accent-custom", color);
      },

      toggleDarkMode: () => {
        set((state) => ({ darkMode: !state.darkMode }));
        get().applyTheme();
      },

      setDarkMode: (enabled) => {
        set({ darkMode: enabled });
        get().applyTheme();
      },

      toggleAnimations: () => {
        set((state) => ({ animations: !state.animations }));
      },

      applyTheme: () => {
        const { theme, darkMode } = get();

        // Handle system theme
        if (theme === "system") {
          const systemDarkMode = window.matchMedia("(prefers-color-scheme: dark)").matches;
          set({ darkMode: systemDarkMode });
          document.documentElement.classList.toggle("dark", systemDarkMode);
          return;
        }

        // Apply theme colors
        const themeConfig = themes[theme];
        const colors = darkMode ? themeConfig.dark : themeConfig.light;

        document.documentElement.classList.toggle("dark", darkMode);

        // Apply CSS custom properties
        Object.entries(colors).forEach(([key, value]) => {
          const cssVar = `--${key.replace(/([A-Z])/g, "-$1").toLowerCase()}`;
          document.documentElement.style.setProperty(cssVar, value);
        });

        // Apply theme data attribute
        document.documentElement.setAttribute("data-theme", theme);
      },
    }),
    {
      name: "theme-storage",
      partialize: (state) => ({
        theme: state.theme,
        accentColor: state.accentColor,
        darkMode: state.darkMode,
        animations: state.animations,
      }),
    }
  )
);

/**
 * Initialize theme on client side
 */
export const initializeTheme = () => {
  if (typeof window === "undefined") return;

  const store = useThemeStore.getState();
  store.applyTheme();

  // Listen for system theme changes
  const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
  const handleChange = () => {
    if (store.theme === "system") {
      store.applyTheme();
    }
  };

  mediaQuery.addEventListener("change", handleChange);
  return () => mediaQuery.removeEventListener("change", handleChange);
};
