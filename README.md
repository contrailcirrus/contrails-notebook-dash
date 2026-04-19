# Contrails Notebook Dashboards

This repository hosts public code and dashboards at <https://dash.contrails.org> to support the [Contrails Notebook](https://notebook.contrails.org/) and other analyses.

## Setup

This repository is an [Observable Framework](https://observablehq.com/framework/) app. To install the required dependencies, run:

```
npm install
```

Then, to start the local preview server, run:

```
npm run dev
```

Then visit <http://localhost:3000> to preview your app.

For more, see <https://observablehq.com/framework/getting-started>.


## Create new dashboard

1. **Copy** the [src/template/](src/@template) directory to a new folder in `src/` named for your dashboard (e.g. `src/new-dashboard/`). Add files and subdirectories for components and data as necessary.
2. **Update** `index.md` in this directory to create your dashboard.
3. **Push** to Github. The [Deploy Action](https://github.com/contrailcirrus/contrails-notebook-dash/blob/main/.github/workflows/deploy.yml) will deploy your new site to <https//dash.contrails.org> (e.g. `dash.contrails.org/new-dashboard/index.html`)

## Update the homepage

New dashboards will not automatically be added to <https://dash.contrails.org>.

[src/index.md](src/index.md) builds into the homepage hosted at `https://dash.contrails.org/index.html`.
Update [src/index.md](src/index.md) to link to your dashboard when ready.

## Embed in Notebook Post

**Embed** a dashboard by pasting the snippet below and updating dashboard `src="https://dash.contrails.org/..."` url in the `<iframe>` below:

```html run=false
<iframe id="dash1" class="gh-article-image" width="100%" height="0" frameborder="0" scrolling="no"  style="border-radius: 5px" src="https://dash.contrails.org/<dashboard>/index.html"></iframe>
<script type="text/javascript">addEventListener("message", (event) => dash1.height = event.data.height);</script>
<noscript>
<!-- default image -->
<img src="https://<path>" width="100%" alt="<alt name>" />
<!-- or -->
<!-- <blockquote>See <a href="https://notebook.contrails.org/<slug>">web version of this post</a> for interactive dashboard.</blockquote> -->
</noscript>
```

### E-mail Newsletter content

Edit the content of the `<noscript>` block to show content in the e-mail newsletter. As its written,
the e-mail version of the Notebook post will show a default image:

```html
<img src="https://<path>" width="100%" alt="<alt name>" />
```

You can also show a blockquote instead:

```md
> See <a href="https://notebook.contrails.org/<slug>">web version of this post</a> for interactive dashboard.
```

Update the Notebook post url with the post `<slug>`.

### Dashboard height

The height of the `<iframe>` is set to "0" so that `<noscript>` tag takes precedence in the e-mail.
The `<script>` tag creates an event listener that will receive a dynamic height from the dashboard
(see [src/@components/observer.js](src/@components/observer.js)).

iframe `id` (`"dash1"` in the example) must match the variable in the event listener (`dash1.height`) to set the height dynamically.

If you have two embeds in the same post, they must have different `id` values.


## Share outside of a notebook

If using the dashboard outside of a notebook context, include this snippet in your dashboard preamble to provide padding on mobile screens:

```css

<style>
  /* If using outside a notebook post, this snippet required for mobile screens */
  @media (min-width: 780px) {
      #observablehq-center {
        margin: 0;
      }
  }
</style>
```

## Observable Project structure

This Framework project looks like this:

```ini
.
├─ src
│  ├─ @components
│  │  ├─ observer.js           # iframe observer for embed
│  │  └─ other.js              # common importable modules
│  ├─ @static
│  │  ├─ 110m.topojson         # common data used across dashboard
│  │  └─ image.svg             # common image used acros dashbaords
│  ├─ example-dashboard1
│  │  ├─ launches.csv.js       # a data loader for dashboard
│  │  ├─ data.json             # a static data file for dashboard
│  │  └─ index.md              # a dashboard page
│  └─ index.md                 # the home page
├─ .gitignore
├─ observablehq.config.js      # the app config file
├─ package.json
└─ README.md
```

**`src`** - This is the “source root” — where your source files live. Pages go here. Each page is a Markdown file. Observable Framework uses [file-based routing](https://observablehq.com/framework/project-structure#routing), which means that the name of the file controls where the page is served. You can create as many pages as you like. Use folders to organize your pages.

**`src/index.md`** - This is the home page for your app. You can have as many additional pages as you’d like, but you should always have a home page, too.

**`src/@components`** - You can put shared [JavaScript modules](https://observablehq.com/framework/imports) anywhere in your source root, but we recommend putting them here. This helps you pull code out of Markdown files and into JavaScript modules, making it easier to reuse code across pages, write tests and run linters, and even share code with vanilla web applications.

**`observablehq.config.js`** - This is the [app configuration](https://observablehq.com/framework/config) file, such as the pages and sections in the sidebar navigation, and the app’s title.


## Command reference

| Command              | Description                                              |
| -------------------- | -------------------------------------------------------- |
| `npm install`        | Install or reinstall dependencies                        |
| `npm run dev`        | Start local preview server                               |
| `npm run build`      | Build your static site, generating `./dist`              |
| `npm run deploy`     | Deploy your app to Observable                            |
| `npm run clean`      | Clear the local data loader cache                        |
| `npm run observable` | Run commands like `observable help`                      |
