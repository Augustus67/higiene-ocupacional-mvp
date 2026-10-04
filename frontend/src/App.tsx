import { FormEvent, useEffect, useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

type TabKey = 'dashboard' | 'noise' | 'chemicals' | 'vibration' | 'heat';

type Company = {
  id: number;
  name: string;
  cnpj?: string;
  description?: string;
};

type Standard = {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
};

type Chemical = {
  id: number;
  name: string;
  cas_number?: string;
  description?: string;
};

function App() {
  const [tab, setTab] = useState<TabKey>('dashboard');
  const [companies, setCompanies] = useState<Company[]>([]);
  const [standards, setStandards] = useState<Standard[]>([]);
  const [chemicals, setChemicals] = useState<Chemical[]>([]);

  const [companyForm, setCompanyForm] = useState({ name: '', cnpj: '', description: '' });
  const [standardForm, setStandardForm] = useState({ name: '', description: '' });
  const [chemicalForm, setChemicalForm] = useState({ name: '', cas_number: '', description: '' });

  const [noiseData, setNoiseData] = useState({
    levels: '85,90,88',
    exposure_hours: '8',
    standard: 'ACGIH',
  });

  const [chemicalData, setChemicalData] = useState({
    standard: 'ACGIH',
    items: 'Acetona: 50, 200; Tolueno: 30, 100',
  });

  const [vibrationData, setVibrationData] = useState({
    acceleration: '4.5',
    exposure_hours: '8',
    vibration_type: 'HAND_ARM',
    standard: 'ACGIH',
  });

  const [heatData, setHeatData] = useState({
    wbgt: '29',
    workload: 'MODERATE',
    standard: 'ACGIH',
  });

  const [noiseResult, setNoiseResult] = useState<any>(null);
  const [chemicalResult, setChemicalResult] = useState<any>(null);
  const [vibrationResult, setVibrationResult] = useState<any>(null);
  const [heatResult, setHeatResult] = useState<any>(null);

  const fetchJson = async <T,>(path: string): Promise<T> => {
    const response = await fetch(`${API_URL}${path}`);
    if (!response.ok) {
      throw new Error(`Erro ao consultar ${path}`);
    }
    return response.json();
  };

  const loadData = async () => {
    try {
      const [companyList, standardList, chemicalList] = await Promise.all([
        fetchJson<Company[]>('/api/companies'),
        fetchJson<Standard[]>('/api/standards'),
        fetchJson<Chemical[]>('/api/chemicals'),
      ]);
      setCompanies(companyList);
      setStandards(standardList);
      setChemicals(chemicalList);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    void loadData();
  }, []);

  const handleCreateCompany = async (event: FormEvent) => {
    event.preventDefault();
    const response = await fetch(`${API_URL}/api/companies`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(companyForm),
    });

    if (response.ok) {
      setCompanyForm({ name: '', cnpj: '', description: '' });
      await loadData();
    }
  };

  const handleCreateStandard = async (event: FormEvent) => {
    event.preventDefault();
    const response = await fetch(`${API_URL}/api/standards`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...standardForm, is_active: true }),
    });

    if (response.ok) {
      setStandardForm({ name: '', description: '' });
      await loadData();
    }
  };

  const handleCreateChemical = async (event: FormEvent) => {
    event.preventDefault();
    const response = await fetch(`${API_URL}/api/chemicals`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(chemicalForm),
    });

    if (response.ok) {
      setChemicalForm({ name: '', cas_number: '', description: '' });
      await loadData();
    }
  };

  const handleNoiseSubmit = async () => {
    const levels = noiseData.levels
      .split(',')
      .map((value) => Number(value.trim()))
      .filter((value) => !Number.isNaN(value));

    const response = await fetch(`${API_URL}/api/noise/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        levels,
        exposure_hours: Number(noiseData.exposure_hours),
        standard: noiseData.standard,
      }),
    });

    setNoiseResult(await response.json());
  };

  const handleChemicalSubmit = async () => {
    const parsedItems = chemicalData.items
      .split(';')
      .map((entry) => entry.trim())
      .filter(Boolean)
      .map((entry) => {
        const [substance, values] = entry.split(':');
        const [concentration, limitValue, limitType = 'TWA'] = (values || '')
          .split(',')
          .map((value) => value.trim());

        return {
          substance: substance.trim(),
          concentration: Number(concentration),
          limit_value: Number(limitValue),
          limit_type: limitType,
        };
      });

    const response = await fetch(`${API_URL}/api/chemicals/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        items: parsedItems,
        standard: chemicalData.standard,
      }),
    });

    setChemicalResult(await response.json());
  };

  const handleVibrationSubmit = async () => {
    const response = await fetch(`${API_URL}/api/vibration/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        acceleration: Number(vibrationData.acceleration),
        exposure_hours: Number(vibrationData.exposure_hours),
        vibration_type: vibrationData.vibration_type,
        standard: vibrationData.standard,
      }),
    });

    setVibrationResult(await response.json());
  };

  const handleHeatSubmit = async () => {
    const response = await fetch(`${API_URL}/api/heat/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        wbgt: Number(heatData.wbgt),
        workload: heatData.workload,
        standard: heatData.standard,
      }),
    });

    setHeatResult(await response.json());
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">MVP</p>
          <h1>Higiene Ocupacional</h1>
        </div>
      </header>

      <nav className="tab-list">
        {['dashboard', 'noise', 'chemicals', 'vibration', 'heat'].map((item) => (
          <button
            key={item}
            className={tab === item ? 'tab active' : 'tab'}
            onClick={() => setTab(item as TabKey)}
          >
            {item === 'dashboard' && 'Dashboard'}
            {item === 'noise' && 'Ruído'}
            {item === 'chemicals' && 'Químicos'}
            {item === 'vibration' && 'Vibração'}
            {item === 'heat' && 'Calor'}
          </button>
        ))}
      </nav>

      <main className="content">
        {tab === 'dashboard' && (
          <section className="panel">
            <h2>Dashboard administrativo</h2>

            <div className="stat-grid">
              <div className="stat-card">
                <span>Empresas</span>
                <strong>{companies.length}</strong>
              </div>
              <div className="stat-card">
                <span>Normas</span>
                <strong>{standards.length}</strong>
              </div>
              <div className="stat-card">
                <span>Substâncias</span>
                <strong>{chemicals.length}</strong>
              </div>
            </div>

            <div className="two-column-grid">
              <form className="card" onSubmit={handleCreateCompany}>
                <h3>Cadastrar empresa</h3>
                <label>
                  Nome
                  <input
                    value={companyForm.name}
                    onChange={(event) => setCompanyForm({ ...companyForm, name: event.target.value })}
                  />
                </label>
                <label>
                  CNPJ
                  <input
                    value={companyForm.cnpj}
                    onChange={(event) => setCompanyForm({ ...companyForm, cnpj: event.target.value })}
                  />
                </label>
                <label>
                  Descrição
                  <textarea
                    rows={3}
                    value={companyForm.description}
                    onChange={(event) => setCompanyForm({ ...companyForm, description: event.target.value })}
                  />
                </label>
                <button type="submit" className="primary">Salvar empresa</button>
              </form>

              <form className="card" onSubmit={handleCreateStandard}>
                <h3>Cadastrar norma</h3>
                <label>
                  Nome
                  <input
                    value={standardForm.name}
                    onChange={(event) => setStandardForm({ ...standardForm, name: event.target.value })}
                  />
                </label>
                <label>
                  Descrição
                  <textarea
                    rows={3}
                    value={standardForm.description}
                    onChange={(event) => setStandardForm({ ...standardForm, description: event.target.value })}
                  />
                </label>
                <button type="submit" className="primary">Salvar norma</button>
              </form>
            </div>

            <div className="card">
              <h3>Listagem rápida</h3>
              <div className="list-group">
                {companies.map((company) => (
                  <div key={company.id} className="mini-item">
                    <strong>{company.name}</strong>
                    <span>{company.cnpj || 'Sem CNPJ'}</span>
                  </div>
                ))}
              </div>
            </div>

            <form className="card" onSubmit={handleCreateChemical}>
              <h3>Cadastrar substância</h3>
              <label>
                Nome
                <input
                  value={chemicalForm.name}
                  onChange={(event) => setChemicalForm({ ...chemicalForm, name: event.target.value })}
                />
              </label>
              <label>
                CAS
                <input
                  value={chemicalForm.cas_number}
                  onChange={(event) => setChemicalForm({ ...chemicalForm, cas_number: event.target.value })}
                />
              </label>
              <label>
                Descrição
                <textarea
                  rows={3}
                  value={chemicalForm.description}
                  onChange={(event) => setChemicalForm({ ...chemicalForm, description: event.target.value })}
                />
              </label>
              <button type="submit" className="primary">Salvar substância</button>
            </form>
          </section>
        )}

        {tab === 'noise' && (
          <section className="panel">
            <h2>Cálculo de Ruído</h2>
            <div className="grid two-columns">
              <label>
                Níveis (dB) - separador por vírgula
                <input
                  value={noiseData.levels}
                  onChange={(event) => setNoiseData({ ...noiseData, levels: event.target.value })}
                />
              </label>
              <label>
                Horas de exposição
                <input
                  type="number"
                  value={noiseData.exposure_hours}
                  onChange={(event) => setNoiseData({ ...noiseData, exposure_hours: event.target.value })}
                />
              </label>
            </div>
            <label>
              Norma
              <select
                value={noiseData.standard}
                onChange={(event) => setNoiseData({ ...noiseData, standard: event.target.value })}
              >
                <option value="ACGIH">ACGIH</option>
                <option value="NR15">NR-15</option>
                <option value="LINARCH">Linarch</option>
              </select>
            </label>
            <button className="primary" onClick={handleNoiseSubmit}>Calcular</button>

            {noiseResult && (
              <div className="result-box">
                <p><strong>Norma:</strong> {noiseResult.standard}</p>
                <p><strong>Leq:</strong> {noiseResult.leq} dB</p>
                <p><strong>Dosagem:</strong> {noiseResult.dose_percent}%</p>
                <p><strong>Limite:</strong> {noiseResult.limit_db} dB</p>
                <p><strong>Status:</strong> {noiseResult.exceeds_limit ? 'Excede' : 'Dentro do limite'}</p>
                <p>{noiseResult.interpretation}</p>
              </div>
            )}
          </section>
        )}

        {tab === 'chemicals' && (
          <section className="panel">
            <h2>Cálculo de Químicos</h2>
            <label>
              Norma
              <select
                value={chemicalData.standard}
                onChange={(event) => setChemicalData({ ...chemicalData, standard: event.target.value })}
              >
                <option value="ACGIH">ACGIH</option>
                <option value="NR15">NR-15</option>
                <option value="LINARCH">Linarch</option>
              </select>
            </label>
            <label>
              Itens no formato: "Substância: concentração, limite, tipo"; separados por ponto-e-vírgula
              <textarea
                rows={5}
                value={chemicalData.items}
                onChange={(event) => setChemicalData({ ...chemicalData, items: event.target.value })}
              />
            </label>
            <button className="primary" onClick={handleChemicalSubmit}>Calcular</button>

            {chemicalResult && (
              <div className="result-box">
                <p><strong>Norma:</strong> {chemicalResult.standard}</p>
                <p><strong>Soma de razões:</strong> {chemicalResult.sum_ratio}</p>
                <p><strong>Máxima razão:</strong> {chemicalResult.max_ratio}</p>
                <p><strong>Status:</strong> {chemicalResult.exceeds_limit ? 'Excede' : 'Dentro do limite'}</p>
                <ul>
                  {chemicalResult.details.map((item: any, index: number) => (
                    <li key={`${item.substance}-${index}`}>
                      {item.substance}: razão {item.ratio} ({item.exceeds ? 'acima' : 'dentro'})
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}

        {tab === 'vibration' && (
          <section className="panel">
            <h2>Cálculo de Vibração</h2>
            <div className="grid two-columns">
              <label>
                Aceleração (m/s²)
                <input
                  type="number"
                  value={vibrationData.acceleration}
                  onChange={(event) => setVibrationData({ ...vibrationData, acceleration: event.target.value })}
                />
              </label>
              <label>
                Horas de exposição
                <input
                  type="number"
                  value={vibrationData.exposure_hours}
                  onChange={(event) => setVibrationData({ ...vibrationData, exposure_hours: event.target.value })}
                />
              </label>
            </div>
            <label>
              Tipo
              <select
                value={vibrationData.vibration_type}
                onChange={(event) => setVibrationData({ ...vibrationData, vibration_type: event.target.value })}
              >
                <option value="HAND_ARM">Mão-braço</option>
                <option value="WHOLE_BODY">Corpo inteiro</option>
              </select>
            </label>
            <label>
              Norma
              <select
                value={vibrationData.standard}
                onChange={(event) => setVibrationData({ ...vibrationData, standard: event.target.value })}
              >
                <option value="ACGIH">ACGIH</option>
                <option value="NR15">NR-15</option>
                <option value="LINARCH">Linarch</option>
              </select>
            </label>
            <button className="primary" onClick={handleVibrationSubmit}>Calcular</button>

            {vibrationResult && (
              <div className="result-box">
                <p><strong>A8:</strong> {vibrationResult.a8} m/s²</p>
                <p><strong>Limite:</strong> {vibrationResult.limit_value} m/s²</p>
                <p><strong>Status:</strong> {vibrationResult.exceeds_limit ? 'Excede' : 'Dentro do limite'}</p>
                <p>{vibrationResult.interpretation}</p>
              </div>
            )}
          </section>
        )}

        {tab === 'heat' && (
          <section className="panel">
            <h2>Cálculo de Calor</h2>
            <div className="grid two-columns">
              <label>
                WBGT (°C)
                <input
                  type="number"
                  value={heatData.wbgt}
                  onChange={(event) => setHeatData({ ...heatData, wbgt: event.target.value })}
                />
              </label>
              <label>
                Esforço físico
                <select
                  value={heatData.workload}
                  onChange={(event) => setHeatData({ ...heatData, workload: event.target.value })}
                >
                  <option value="LIGHT">Leve</option>
                  <option value="MODERATE">Moderado</option>
                  <option value="HEAVY">Pesado</option>
                  <option value="VERY_HEAVY">Muito pesado</option>
                </select>
              </label>
            </div>
            <label>
              Norma
              <select
                value={heatData.standard}
                onChange={(event) => setHeatData({ ...heatData, standard: event.target.value })}
              >
                <option value="ACGIH">ACGIH</option>
                <option value="NR15">NR-15</option>
                <option value="LINARCH">Linarch</option>
              </select>
            </label>
            <button className="primary" onClick={handleHeatSubmit}>Calcular</button>

            {heatResult && (
              <div className="result-box">
                <p><strong>WBGT:</strong> {heatResult.wbgt} °C</p>
                <p><strong>Limite:</strong> {heatResult.allowable_limit} °C</p>
                <p><strong>Status:</strong> {heatResult.exceeds_limit ? 'Excede' : 'Dentro do limite'}</p>
                <p>{heatResult.interpretation}</p>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
