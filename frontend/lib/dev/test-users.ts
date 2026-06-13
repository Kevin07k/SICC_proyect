export interface TestUser {
  uuid: string;
  email: string;
  nombre: string;
  rol: string;
  sede: string;
  id_sede: number;
}

export const TEST_USERS: TestUser[] = [
  {
    uuid: "11111111-1111-1111-1111-111111111101",
    email: "admin@sicc.com",
    nombre: "Administrador del Sistema",
    rol: "Administrador",
    sede: "Santa Cruz (Central)",
    id_sede: 1,
  },
  {
    uuid: "11111111-1111-1111-1111-111111111102",
    email: "analista.sc@test.sicc",
    nombre: "Analista Santa Cruz",
    rol: "Analista",
    sede: "Santa Cruz (Central)",
    id_sede: 1,
  },
  {
    uuid: "11111111-1111-1111-1111-111111111103",
    email: "analista.cb@test.sicc",
    nombre: "Analista Cochabamba",
    rol: "Analista",
    sede: "Cochabamba",
    id_sede: 2,
  },
  {
    uuid: "11111111-1111-1111-1111-111111111104",
    email: "dba@test.sicc",
    nombre: "DBA Central",
    rol: "DBA",
    sede: "Santa Cruz (Central)",
    id_sede: 1,
  },
  {
    uuid: "11111111-1111-1111-1111-111111111105",
    email: "dba.cb@test.sicc",
    nombre: "DBA Cochabamba",
    rol: "DBA",
    sede: "Cochabamba",
    id_sede: 2,
  },
];

export const DEV_SWITCHER_ENABLED =
  process.env.NEXT_PUBLIC_ENABLE_DEV_SWITCHER === "true";
