/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    content: [
        './tailwind_app/static_src/**/*.{html,js,jsx,ts,tsx}',
        '../templates/**/*.html',
        '../../templates/**/*.html',
        '../../**/templates/**/*.html',
        // Templates within theme app (e.g. base.html)
        '../templates/**/*.html',
        // Templates in other apps
        '../../templates/**/*.html',
        // Ignore files in node_modules
        '!../../**/node_modules',
        // Include JavaScript files that might contain Tailwind CSS classes
        '../../**/*.js',
        // Include Python files that might contain Tailwind CSS classes
        '../../**/*.py'

        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your project structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the project. */
        // '../../**/*.js',

        /**
         * Python: If you use Tailwind CSS classes in Python, uncomment the following line
         * and make sure the pattern below matches your project structure.
         */
        // '../../**/*.py'
    ],
    theme: {
        extend: {
          fontFamily: {
            ubuntu: ["Ubuntu", "sans-serif"],
            poppins: ["Poppins", "sans-serif"],
          },
          width: {
            100: "100%",
            120: "120%",
            240: "240%",
            '1/4vw': '25vw',
            '1/2vw': '50vw',
            '3/4vw': '75vw',
            'fullvw': '100vw',
          },
          height: {
            '1/4vh': '25vh',
            '1/2vh': '50vh',
            '3/4vh': '75vh',
            'fullvh': '100vh',
          },
          container: {
            padding: {
              xxs: "0.5rem",
              xs: "1rem",
              DEFAULT: "1rem",
              sm: "1rem",
              lg: "2rem",
              xl: "3rem",
              "4xl": "6rem",
            },
          },
          screens: {
            xxs: "210px",
            xs: "320px",
            xsd: "375px",
            xsdd: "568px",
            sm: "640px",
            md: "768px",
            lg: "1024px",
            xl: "1280px",
            xxl: "1536px",
            xxxl: "1920px",
            mobile: { max: "639px" },
            small_tablet: { min: "640px"},
            tablet: { min: "768px"},
            desktop: { min: "1024px" },
            "desktop-lg": { min: "1280px" },
            "desktop-xl": { min: "1536px" },
            "desktop-xxl": { min: "1920px" },
          },
          colors: {
            light: {
              basic_bg: "#f9fafb",
              basic_text: "#041322",
              hover: {
                primary: "#5a67d8", // Hover color for primary elements in light mode
                secondary: "#f3f4f6", // Hover color for secondary elements in light mode
                // Add more hover colors as needed
              },
              shadow: {
                primary: "#f3f4f6", // Shadow color for primary elements in light mode
                secondary: "#cbccce", // Shadow color for secondary elements in light mode
                // Add more shadow colors as needed
              },
              accent: "#8a16bc",
              accent2: "#99f6e4",
              accent3: "#08EEE0",
              tretiary: "#20B2AA",
              forthiary: "#059C3D",
            },
            // accent: "#4169e1",
            maire: "#1D1D1B",
            blackcurrant: "#1C1B1D",
            whiteSmoke: "#F5F5F5",
            "gradient-color-1": "rgb(138, 2, 188)",
            "gradient-color-2": "rgb(153, 246, 228)",
            LightSeaGreen: "#20B2AA",
            dark_blue: "#0E1724",
            magic_mint: "#95F3C6",
            mint_cream: "#f9fffe",
            black_pearl: "#041322",
            tufts_blue: "#008DD9",
            greenish: "#059C3D",
            test: "#00c8d2",
            test1: "#75b747",
            test2: "#5147b7",
            test3: "#b74775",
            test4: "#47adb7",
            test5: "#4775b7",
            royal_blue: "#4169e1",
            true_blue: "#2d68c4",
            yale_blue_shade: "#08457E",
          },
          boxShadow: {
            "inner-custom":
              "inset 0 10px 10px -3px rgba(0, 0, 0, 0.1), inset 0 4px 3px -2px rgba(0, 0, 0, 0.05)",
          },
          backgroundImage: {
            custom: "url('/static/images/Vector4.png')",
          },
        },
        variants: {
          extend: {
            backgroundColor: ["active"],
            textColor: ["active"],
            borderColor: ["active"],
            borderWidth: ["active"],
            display: ["group-hover"],
            visibility: ["group-hover"],
            scale: ["group-hover"],
            translate: ["group-hover"],
            rotate: ["group-hover"],
            transform: ["group-hover"],
            opacity: ["group-hover"],
            cursor: ["disabled"],
            pointerEvents: ["disabled"],
            fill: ["group-hover"],
          },
        },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}}
