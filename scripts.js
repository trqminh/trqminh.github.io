document.addEventListener('DOMContentLoaded', loadPublications);

async function loadPublications() {
    const container = document.querySelector('[data-publications]');
    if (!container) return;

    try {
        const source = container.dataset.source || 'publications.json';
        const response = await fetch(source);

        if (!response.ok) {
            throw new Error(`Publication request failed with status ${response.status}`);
        }

        const data = await response.json();
        if (!Array.isArray(data.publications)) {
            throw new Error('Publication data is not an array');
        }

        const publications = container.dataset.filter === 'selected'
            ? data.publications.filter((publication) => publication.selected === 1)
            : data.publications;

        renderPublications(container, publications);
    } catch (error) {
        console.error('Failed to load publications:', error);
        container.replaceChildren(createStatus('Unable to load publications.', 'publication-error'));
    }
}

function renderPublications(container, publications) {
    if (publications.length === 0) {
        container.replaceChildren(createStatus('No publications found.', 'publication-status'));
        return;
    }

    const fragment = document.createDocumentFragment();

    if (container.dataset.group === 'true') {
        groupPublications(publications).forEach(([group, entries]) => {
            fragment.appendChild(createGroupHeading(group));
            entries.forEach((publication) => {
                fragment.appendChild(createPublication(publication));
            });
        });
    } else {
        publications.forEach((publication) => {
            fragment.appendChild(createPublication(publication));
        });
    }

    container.replaceChildren(fragment);
}

function groupPublications(publications) {
    const groups = new Map();

    publications.forEach((publication) => {
        const name = publication.group || 'Other';
        if (!groups.has(name)) groups.set(name, []);
        groups.get(name).push(publication);
    });

    return [...groups];
}

function createGroupHeading(name) {
    const heading = document.createElement('h2');
    heading.className = 'publication-group';
    heading.textContent = name;
    return heading;
}

function createPublication(publication) {
    const entry = document.createElement('article');
    entry.className = 'publication-entry';

    if (publication.thumbnail) {
        const thumbnail = document.createElement('img');
        thumbnail.className = 'publication-thumbnail';
        thumbnail.src = publication.thumbnail;
        thumbnail.alt = `${publication.title || 'Publication'} preview`;
        thumbnail.loading = 'lazy';
        thumbnail.addEventListener('click', () => openLightbox(publication.thumbnail, publication.title));
        entry.appendChild(thumbnail);
    }

    const content = document.createElement('div');
    content.className = 'publication-content';

    const title = document.createElement('strong');
    title.className = 'publication-title';
    title.textContent = publication.title || 'Untitled publication';
    content.appendChild(title);

    if (Array.isArray(publication.authors) && publication.authors.length > 0) {
        content.appendChild(createAuthors(publication.authors));
    }

    if (publication.venue || publication.award) {
        const venue = document.createElement('p');
        venue.className = 'publication-venue';

        if (publication.venue) {
            venue.appendChild(document.createTextNode(publication.venue));
        }

        if (publication.award) {
            if (publication.venue) venue.appendChild(document.createTextNode(' — '));
            const award = document.createElement('span');
            award.className = 'publication-award';
            award.textContent = publication.award;
            venue.appendChild(award);
        }

        content.appendChild(venue);
    }

    const links = createLinks(publication.links);
    if (links) content.appendChild(links);

    entry.appendChild(content);
    return entry;
}

function createAuthors(authors) {
    const authorLine = document.createElement('p');
    authorLine.className = 'publication-authors';

    authors.forEach((author, index) => {
        const authorNode = document.createElement(author.includes('Minh Tran') ? 'strong' : 'span');
        if (author.includes('Minh Tran')) authorNode.className = 'highlight-name';
        authorNode.textContent = author;
        authorLine.appendChild(authorNode);

        if (index < authors.length - 1) {
            authorLine.appendChild(document.createTextNode(', '));
        }
    });

    return authorLine;
}

function createLinks(links) {
    if (!links || typeof links !== 'object') return null;

    const linkDefinitions = [
        ['pdf', 'PDF'],
        ['code', 'Code'],
        ['project', 'Project page'],
        ['demo', 'Demo']
    ];
    const availableLinks = linkDefinitions.filter(([key]) => links[key]);

    if (availableLinks.length === 0) return null;

    const linkLine = document.createElement('p');
    linkLine.className = 'publication-links';

    availableLinks.forEach(([key, label]) => {
        const link = document.createElement('a');
        link.href = links[key];
        link.textContent = label;
        linkLine.appendChild(link);
    });

    return linkLine;
}

function createStatus(message, className) {
    const status = document.createElement('p');
    status.className = className;
    status.textContent = message;
    return status;
}

function openLightbox(src, title) {
    const overlay = document.createElement('div');
    overlay.className = 'lightbox-overlay';

    const img = document.createElement('img');
    img.className = 'lightbox-image';
    img.src = src;
    img.alt = title || 'Preview';

    overlay.appendChild(img);
    document.body.appendChild(overlay);

    requestAnimationFrame(() => overlay.classList.add('lightbox-visible'));

    function close() {
        overlay.classList.remove('lightbox-visible');
        overlay.addEventListener('transitionend', () => overlay.remove(), { once: true });
        document.removeEventListener('keydown', onKey);
    }

    function onKey(e) {
        if (e.key === 'Escape') close();
    }

    overlay.addEventListener('click', close);
    document.addEventListener('keydown', onKey);
}
