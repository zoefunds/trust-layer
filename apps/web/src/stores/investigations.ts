import { create } from "zustand";
import { Investigation, Validator, ValidatorType, ValidatorStatus } from "@/types";
import { investigationsApi } from "@/lib/api";

interface InvestigationsState {
  investigations: Investigation[];
  current: Investigation | null;
  isLoading: boolean;
  isCreating: boolean;
  fetchAll: () => Promise<void>;
  fetchOne: (id: string) => Promise<void>;
  create: (protocolName: string) => Promise<Investigation>;
  updateValidator: (investigationId: string, validatorType: ValidatorType, update: Partial<Validator>) => void;
  setCurrentStatus: (status: Investigation["status"]) => void;
}

export const useInvestigationsStore = create<InvestigationsState>((set, get) => ({
  investigations: [],
  current: null,
  isLoading: false,
  isCreating: false,

  fetchAll: async () => {
    set({ isLoading: true });
    try {
      const { data } = await investigationsApi.list();
      set({ investigations: data });
    } finally {
      set({ isLoading: false });
    }
  },

  fetchOne: async (id) => {
    set({ isLoading: true });
    try {
      const { data } = await investigationsApi.get(id);
      set({ current: data });
    } finally {
      set({ isLoading: false });
    }
  },

  create: async (protocolName) => {
    set({ isCreating: true });
    try {
      const { data } = await investigationsApi.create(protocolName);
      set((state) => ({
        investigations: [data, ...state.investigations],
        current: data,
      }));
      return data;
    } finally {
      set({ isCreating: false });
    }
  },

  updateValidator: (investigationId, validatorType, update) => {
    set((state) => {
      if (!state.current || state.current.id !== investigationId) return state;
      const validators = state.current.validators.map((v) =>
        v.validator_type === validatorType ? { ...v, ...update } : v
      );
      return { current: { ...state.current, validators } };
    });
  },

  setCurrentStatus: (status) => {
    set((state) => {
      if (!state.current) return state;
      return { current: { ...state.current, status } };
    });
  },
}));
