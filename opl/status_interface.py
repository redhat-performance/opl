from abc import ABC, abstractmethod

class IStatusData(ABC):
    
    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def __getitem__(self, key):
        pass

    @abstractmethod
    def __setitem__(self, key, value):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass
    
    @abstractmethod
    def __gt__(self, other):
        pass

    @abstractmethod
    def _split_mutlikey(self, multikey):
        pass
    
    @abstractmethod
    def _get(self, data, split_key):
        pass
    
    @abstractmethod
    def get(self, multikey):
        pass
    
    @abstractmethod
    def get_date(self, multikey):
        pass

    @abstractmethod
    def _set(self, data, split_key, value):
        pass
    
    @abstractmethod
    def set(self, multikey, value):
        pass
    
    @abstractmethod
    def set_now(self, multikey):
        pass
    
    @abstractmethod
    def set_subtree_json(self, multikey, file_path):
        pass

    @abstractmethod
    def _remove(self, data, split_key):
        pass

    @abstractmethod
    def remove(self, multikey):
        pass

    @abstractmethod
    def list(self, multikey):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def info(self):
        pass

    @abstractmethod
    def dump(self):
        pass

    @abstractmethod
    def save(self, filename=None):
        pass
    
    @abstractmethod
    def _save(self, filename):
        pass