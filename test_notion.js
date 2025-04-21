// Jednoduchý skript pro test připojení k Notion API
const https = require('https');

// API klíč
const apiKey = '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';

// Nastavení požadavku
const options = {
  hostname: 'api.notion.com',
  path: '/v1/users/me',
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
  }
};

console.log('Testuji připojení k Notion API...');

// Odeslání požadavku
const req = https.request(options, (res) => {
  let data = '';

  // Přijímání dat
  res.on('data', (chunk) => {
    data += chunk;
  });

  // Dokončení požadavku
  res.on('end', () => {
    if (res.statusCode === 200) {
      const response = JSON.parse(data);
      console.log('Připojení k Notion API je funkční!');
      console.log(`Přihlášený uživatel: ${response.name}`);
      console.log(`ID uživatele: ${response.id}`);
      console.log('\nKompletní odpověď:');
      console.log(JSON.stringify(response, null, 2));
    } else {
      console.log(`Chyba při připojení k Notion API: ${res.statusCode}`);
      console.log(data);
    }
  });
});

// Zpracování chyb
req.on('error', (error) => {
  console.error(`Neočekávaná chyba: ${error.message}`);
});

// Ukončení požadavku
req.end();
