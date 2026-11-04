from shopbot import knowledge


def test_documents_follow_the_database_to_another_machine(monkeypatch,tmp_path):
    keys=[]
    for name in ('shop-machine','docker'):
        root=tmp_path/name;(root/'data').mkdir(parents=True)
        monkeypatch.setattr(knowledge,'ROOT',root)
        keys.append(knowledge.namespace(root/'data/shop.sqlite'))
    assert keys[0]==keys[1]


def test_databases_keep_their_own_documents(tmp_path):
    assert knowledge.namespace(tmp_path/'a.sqlite')!=knowledge.namespace(tmp_path/'b.sqlite')
    assert knowledge.namespace(knowledge.ROOT/'data/a.sqlite')!=knowledge.namespace(knowledge.ROOT/'data/b.sqlite')
