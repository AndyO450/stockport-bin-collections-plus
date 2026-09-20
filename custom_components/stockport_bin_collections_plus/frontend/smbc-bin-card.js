class SmbcBinCard extends HTMLElement {
  static getStubConfig() {
    return { title: "SMBC bin collections" };
  }

  static getConfigForm() {
    return {
      schema: [
        { name: "title", selector: { text: {} } },
        {
          name: "entities",
          selector: {
            entity: { domain: "sensor", multiple: true },
          },
        },
      ],
      computeLabel: (schema) =>
        ({ title: "Title", entities: "Bin date sensors (optional)" })[
          schema.name
        ] || schema.name,
    };
  }

  setConfig(config) {
    this.config = {
      title: "SMBC bin collections",
      ...config,
    };
    if (!this.shadowRoot) this.attachShadow({ mode: "open" });
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 4;
  }

  getGridOptions() {
    return { columns: 12, rows: 3, min_rows: 3 };
  }

  _entities() {
    const configured = Array.isArray(this.config?.entities)
      ? this.config.entities
      : [];
    const ids = configured.length
      ? configured
      : Object.keys(this._hass?.states || {}).filter(
          (entityId) =>
            entityId.startsWith(
              "sensor.stockport_bin_collections_plus_"
            ) && entityId.includes("_bin")
        );

    const order = { blue: 0, brown: 1, green: 2, black: 3 };
    return ids
      .map((entityId) => this._hass.states[entityId])
      .filter(Boolean)
      .sort(
        (a, b) =>
          (order[this._colour(a.entity_id)] ?? 99) -
          (order[this._colour(b.entity_id)] ?? 99)
      );
  }

  _colour(entityId) {
    return ["blue", "brown", "green", "black"].find((colour) =>
      entityId.includes(`_${colour}_bin`)
    );
  }

  _formatDate(value) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value || "")) return value || "Unknown";
    const date = new Date(`${value}T12:00:00`);
    return new Intl.DateTimeFormat(this._hass?.locale?.language || "en-GB", {
      weekday: "short",
      day: "numeric",
      month: "short",
    }).format(date);
  }

  _formatCardDate(value) {
    const shortDate = this._formatDate(value).replace(/^[A-Za-z]{3},?\s/, "");
    if (value === this._localIsoDate(0)) return `Today · ${shortDate}`;
    if (value === this._localIsoDate(1)) return `Tomorrow · ${shortDate}`;
    return this._formatDate(value);
  }

  _description(colour) {
    return {
      blue: "Paper & card",
      brown: "Plastic & glass",
      green: "Food & garden",
      black: "General waste",
    }[colour] || "Household waste";
  }

  _localIsoDate(offsetDays = 0) {
    const date = new Date();
    date.setHours(12, 0, 0, 0);
    date.setDate(date.getDate() + offsetDays);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  _summary(entities) {
    const dated = entities
      .filter((entity) => /^\d{4}-\d{2}-\d{2}$/.test(entity.state))
      .sort((a, b) => a.state.localeCompare(b.state));
    if (!dated.length) {
      return { date: "Date unavailable", bins: [], action: "Check the integration status", urgent: false };
    }

    const nextDate = dated[0].state;
    const nextBins = dated.filter((entity) => entity.state === nextDate);
    const names = nextBins.map((entity) => {
      const colour = this._colour(entity.entity_id);
      return colour ? colour[0].toUpperCase() + colour.slice(1) : "Bin";
    });
    if (nextDate === this._localIsoDate(0)) {
      return { date: this._formatDate(nextDate), bins: names, action: "Collection is today", urgent: true };
    }
    if (nextDate === this._localIsoDate(1)) {
      return { date: this._formatDate(nextDate), bins: names, action: "Put these bins out tonight", urgent: true };
    }

    const daysAway = Math.round(
      (new Date(`${nextDate}T12:00:00`) - new Date(`${this._localIsoDate()}T12:00:00`)) /
        86400000
    );
    return {
      date: this._formatDate(nextDate),
      bins: names,
      action: daysAway <= 7 ? "Coming up this week" : "",
      urgent: false,
    };
  }

  _escape(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  _showMoreInfo(entityId) {
    const event = new CustomEvent("hass-more-info", {
      bubbles: true,
      composed: true,
      detail: { entityId },
    });
    this.dispatchEvent(event);
  }

  _render() {
    if (!this.shadowRoot || !this._hass || !this.config) return;
    const entities = this._entities();
    const title = this.config.title || "SMBC bin collections";
    const summary = this._summary(entities);

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        ha-card { padding: 16px; overflow: hidden; }
        .header {
          display: flex; align-items: center; gap: 10px;
          margin: 0 2px 14px; font-size: 20px; font-weight: 650;
        }
        .header ha-icon { color: var(--primary-color); }
        .summary {
          margin-bottom: 12px; padding: 14px 16px; border-radius: 14px;
          background: rgba(3,169,244,.10); border: 1px solid rgba(3,169,244,.25);
        }
        .summary.urgent { background: rgba(255,152,0,.17); border-color: rgba(255,152,0,.38); }
        .summary-kicker { color: var(--secondary-text-color); font-size: 11px; font-weight: 750; letter-spacing: .08em; text-transform: uppercase; }
        .summary-date { margin-top: 3px; font-size: 23px; font-weight: 750; line-height: 1.2; }
        .summary-bins { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
        .summary-bin { --bin-color: #607d8b; display: inline-flex; align-items: center; gap: 5px; font-size: 12px; font-weight: 700; }
        .summary-bin ha-icon { color: var(--bin-color); --mdc-icon-size: 23px; }
        .summary-bin.blue { --bin-color: #2196f3; }
        .summary-bin.brown { --bin-color: #a4715b; }
        .summary-bin.green { --bin-color: #4caf50; }
        .summary-bin.black { --bin-color: #9e9e9e; }
        .summary-action { margin-top: 10px; color: #ffb300; font-size: 13px; font-weight: 700; }
        .grid {
          display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 10px;
        }
        .bin {
          --bin-color: #607d8b; --bin-bg: rgba(96,125,139,.17);
          appearance: none; border: 1px solid color-mix(in srgb, var(--bin-color) 45%, transparent);
          border-radius: 14px; background: var(--bin-bg); color: var(--primary-text-color);
          min-height: 94px; padding: 12px; cursor: pointer; text-align: left;
          display: grid; grid-template-columns: 42px 1fr; align-items: center; gap: 10px;
          transition: transform .12s ease, filter .12s ease;
        }
        .bin:hover { filter: brightness(1.08); transform: translateY(-1px); }
        .bin:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 2px; }
        .bin ha-icon { color: var(--bin-color); --mdc-icon-size: 34px; }
        .name { font-size: 15px; font-weight: 700; text-transform: capitalize; }
        .date { margin-top: 5px; font-size: 14px; font-weight: 600; color: var(--secondary-text-color); }
        .description { margin-top: 3px; font-size: 12px; color: var(--secondary-text-color); }
        .blue { --bin-color: #2196f3; --bin-bg: rgba(33,150,243,.18); }
        .brown { --bin-color: #9b6a55; --bin-bg: rgba(121,85,72,.22); }
        .green { --bin-color: #43a047; --bin-bg: rgba(76,175,80,.18); }
        .black { --bin-color: #9e9e9e; --bin-bg: rgba(90,90,90,.25); }
        .empty { color: var(--secondary-text-color); padding: 8px 2px 4px; }
        @media (max-width: 420px) {
          .grid { grid-template-columns: 1fr; }
        }
      </style>
      <ha-card>
        <div class="header"><ha-icon icon="mdi:trash-can-outline"></ha-icon>${this._escape(title)}</div>
        <div class="summary ${summary.urgent ? "urgent" : ""}">
          <div class="summary-kicker">Next collection</div>
          <div class="summary-date">${this._escape(summary.date)}</div>
          <div class="summary-bins">${summary.bins.map((name) => `<span class="summary-bin ${name.toLowerCase()}"><ha-icon icon="mdi:trash-can"></ha-icon>${this._escape(name)}</span>`).join("")}</div>
          ${summary.action ? `<div class="summary-action">${this._escape(summary.action)}</div>` : ""}
        </div>
        ${entities.length ? `<div class="grid">${entities
          .map((entity) => {
            const colour = this._colour(entity.entity_id) || "";
            const name = entity.attributes.friendly_name
              ?.replace(/^Stockport bin collections Plus\s*/i, "") ||
              `${colour} bin`;
            return `<button class="bin ${colour}" data-entity="${entity.entity_id}">
              <ha-icon icon="mdi:trash-can"></ha-icon>
              <span><div class="name">${this._escape(name)}</div><div class="date">${this._escape(this._formatCardDate(entity.state))}</div><div class="description">${this._escape(this._description(colour))}</div></span>
            </button>`;
          })
          .join("")}</div>` : `<div class="empty">No Stockport bin date sensors found. Configure the integration first, or select the sensors in the card editor.</div>`}
      </ha-card>`;

    this.shadowRoot.querySelectorAll(".bin").forEach((button) => {
      button.addEventListener("click", () =>
        this._showMoreInfo(button.dataset.entity)
      );
    });
  }
}

if (!customElements.get("smbc-bin-card")) {
  customElements.define("smbc-bin-card", SmbcBinCard);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "smbc-bin-card")) {
  window.customCards.push({
    type: "smbc-bin-card",
    name: "SMBC Bin Card",
    description: "Colour-coded Stockport bin collection dates.",
    preview: true,
    documentationURL:
      "https://github.com/AndyO450/stockport-bin-collections-plus#smbc-bin-card",
    getEntitySuggestion: (_hass, entityId) =>
      entityId.startsWith("sensor.stockport_bin_collections_plus_")
        ? { entities: [entityId] }
        : null,
  });
}
